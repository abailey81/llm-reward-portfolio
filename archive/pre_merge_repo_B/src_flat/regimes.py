"""HMM regime detection with leakage guards baked in (Pillar IV; ADR-011).

Protocol (config inference.regimes; harvest-verified): 3-state Gaussian HMM, EM with 10
restarts keeping max log-likelihood, FIT ON TRAIN ONLY, FILTERED probabilities
P(z_t | data_{1:t}) — never smoothed — and shift(1) before any decision/labelling use.
Anchors: Hamilton (1989); LSEG regime-detection worked example (shift convention);
Bulla et al. (2011) rolling protocol.

The filtering is implemented HERE as an explicit scaled forward recursion over the
fitted model's public parameters (startprob_, transmat_, means_, covars_) rather than
through hmmlearn private APIs (`_do_forward_pass` et al.): (i) private APIs drift
across versions; (ii) hmmlearn's `predict_proba` is SMOOTHED (forward–backward) and
using it would leak future information into regime features (R3). Filtered-ness is
unit-tested by truncation invariance — probabilities at t must not change when data
after t changes (`tests/test_regimes.py`), a test smoothed probabilities fail.

Requires `hmmlearn` for EM fitting only (imported lazily so the rest of the package
works without it).
"""
from __future__ import annotations

import numpy as np

from .config import get


class GaussianHMMRegimes:
    def __init__(self, n_states: int | None = None, em_restarts: int | None = None, seed: int = 0):
        cfg = get("inference.regimes.hmm")
        self.n_states = int(n_states or cfg["n_states"])
        self.em_restarts = int(em_restarts or cfg["em_restarts"])
        self.cov_type = cfg["covariance_type"]
        self.seed = seed
        self._model = None

    def fit(self, train_returns: np.ndarray) -> "GaussianHMMRegimes":
        """Fit on the TRAINING WINDOW ONLY (R3). Keeps the best of em_restarts fits."""
        try:
            from hmmlearn.hmm import GaussianHMM
        except ImportError as e:  # pragma: no cover
            raise ImportError("pip install hmmlearn (requirements.txt)") from e
        x = np.asarray(train_returns, dtype=float).reshape(-1, 1)
        best, best_ll = None, -np.inf
        for k in range(self.em_restarts):
            m = GaussianHMM(
                n_components=self.n_states, covariance_type=self.cov_type,
                n_iter=200, random_state=self.seed + k,
            )
            try:
                m.fit(x)
                ll = m.score(x)
            except Exception:
                continue
            if ll > best_ll:
                best, best_ll = m, ll
        if best is None:
            raise RuntimeError("all EM restarts failed")
        self._model = best
        return self

    # ------------------------------------------------------------- fitted parameters
    def _emission_params(self) -> tuple[np.ndarray, np.ndarray]:
        """Per-state (mean, variance) for the 1-D observation, robust to the
        covariance_type layout (full: (k,1,1); diag: (k,1); spherical: (k,))."""
        means = np.asarray(self._model.means_, dtype=float).reshape(self.n_states)
        covs = np.asarray(self._model.covars_, dtype=float)
        variances = np.array([float(np.atleast_2d(covs[k])[0, 0]) for k in range(self.n_states)])
        return means, variances

    def _log_emission(self, x: np.ndarray) -> np.ndarray:
        """(T, k) Gaussian log-densities of each observation under each state."""
        means, variances = self._emission_params()
        variances = np.maximum(variances, 1e-300)
        x = x.reshape(-1, 1)
        return -0.5 * (np.log(2.0 * np.pi * variances) + (x - means) ** 2 / variances)

    # --------------------------------------------------------------------- filtering
    def filtered_probs_shifted(self, returns: np.ndarray) -> np.ndarray:
        """FILTERED P(z_t | r_{1:t}) via the scaled forward recursion, then shift(1):
        row t carries information through t-1 only; row 0 is uniform.

        NEVER substitute hmmlearn's predict_proba here — it is SMOOTHED
        (forward-backward, conditions on the FULL sample) and would leak (R3).
        Leakage posture: row t of the output uses only returns[0:t].
        """
        if self._model is None:
            raise RuntimeError("fit() first (on the training window only)")
        x = np.asarray(returns, dtype=float).ravel()
        if x.size == 0:
            raise ValueError("returns must be non-empty")
        log_b = self._log_emission(x)                      # (T, k)
        startprob = np.asarray(self._model.startprob_, dtype=float)
        transmat = np.asarray(self._model.transmat_, dtype=float)

        t_len = x.shape[0]
        filtered = np.empty((t_len, self.n_states))
        # alpha_0 ∝ pi_k * b_k(x_0); per-step normalisation = scaled forward algorithm
        b0 = np.exp(log_b[0] - log_b[0].max())
        a = startprob * b0
        a_sum = a.sum()
        a = a / a_sum if a_sum > 0 else np.full(self.n_states, 1.0 / self.n_states)
        filtered[0] = a
        for t in range(1, t_len):
            predict = a @ transmat                          # P(z_t | r_{1:t-1})
            bt = np.exp(log_b[t] - log_b[t].max())
            a = predict * bt
            a_sum = a.sum()
            a = a / a_sum if a_sum > 0 else np.full(self.n_states, 1.0 / self.n_states)
            filtered[t] = a

        shifted = np.vstack([np.full((1, self.n_states), 1.0 / self.n_states), filtered[:-1]])
        return shifted

    def label_states_by_volatility(self) -> np.ndarray:
        """Order states by conditional volatility (low->high) for bull/neutral/crisis naming."""
        if self._model is None:
            raise RuntimeError("fit() first")
        _, variances = self._emission_params()
        return np.argsort(np.sqrt(variances))

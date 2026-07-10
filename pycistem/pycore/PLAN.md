# pycore: pure-Python reimplementation of pycistem.core

Goal: remove the need to compile the cisTEM C++ extension (`pycistem.core`,
built from `pycistem/core/{core,database,euler_search,run_profiles}.cpp`)
for anything the rest of this repo actually uses. Each reimplementation
lives in `pycistem.pycore` and is validated against the compiled extension
in `tests/pycore/` (skipped automatically if `pycistem.core` isn't
importable).

## Inventory

`pycistem.core` exposes ~25 pybind11 classes. Grouped by how they're
actually used outside of `pycistem/core/`:

### Tier A — blocks normal package usage today (done, wired in)

Small, no FFT/physics. Currently imported lazily inside functions in
`pycistem/database/__init__.py` and `pycistem/programs/match_template.py`
specifically so the rest of the package can be imported without the
compiled extension.

- `ParameterMap` — 5 bool fields (`phi`, `theta`, `psi`, `x_shift`,
  `y_shift`), `SetAllTrue()`. Source: `cisTEM/src/core/particle.{h,cpp}`.
- `EulerSearch` — grid search position counting. Used methods/attrs:
  `InitGrid(...)`, `CalculateGridSearchPositions(bool)`,
  `theta_max` (r/w), `number_of_search_positions` (r), `test_mirror` (r).
  `Run()` uses the full `Image`/FFT engine (Tier B) and is not used
  anywhere in this repo — left unimplemented (raises `NotImplementedError`).
  Source: `cisTEM/src/core/euler_search.{h,cpp}`.
- `RunCommand`, `RunProfile`, `RunProfileManager` — plain data containers
  for cluster/queue run profiles (add/remove commands, disk import/export).
  Source: `cisTEM/src/core/run_{command,profile,profile_manager}.{h,cpp}`.
- `Database` (thin slice only) — the C++ class has 350+ methods; only
  these are ever called from Python: `CreateNewDatabase`, `Open`, `Close`,
  `CreateAllTables`, `ExecuteSQL`, `ReturnSingleLongFromSelectCommand`,
  `GetMasterSettings`, `BeginMovieAssetInsert`/`AddNextMovieAsset`/
  `EndMovieAssetInsert`, `CheckandUpdateSchema` (no-op placeholder — schema
  migration across historical schema versions is out of scope for now).
  Everything else in `pycistem/database/__init__.py` already talks to
  sqlite3 directly, so the C++ Database class is mostly redundant already.
  Schema DDL captured by dumping `.schema` from a project created by the
  compiled extension (26 tables) — see `_database.py::SCHEMA_SQL`.
- `Project` — `CreateNewProject`, `OpenProjectFromFile`, `Close`,
  `.database` property, directory scaffolding under `Assets/`.
  Source: `cisTEM/src/core/project.{h,cpp}`.

`pycistem/database/__init__.py` and `pycistem/programs/match_template.py`
now import `Project`/`EulerSearch`/`ParameterMap` from `pycistem.pycore`
directly (no more `from pycistem.core import ...`) — verified end-to-end
with `pycistem.core` blocked entirely via a `sys.meta_path` finder.

### Tier B — only exercised in tests/examples and disabled prototype code

The actual numerical engine (FFTW-backed real/complex image arithmetic,
CTF physics). Not on the critical path for the live pipeline (which
shells out to compiled cisTEM *executables* over sockets — see
`pycistem/programs/cistem_program.py`), but needed to re-enable
`tests/test_core.py`, `examples/test_extract_slice.py`, and the
commented-out `Image` usage in `programs/refine_ctf.py` /
`programs/estimate_beamtilt.py`.

- `AnglesAndShifts` — Euler/rotation matrix generation.
- `CTF` — 15-parameter physics model (defocus, aberration, envelope,
  phase shift). `Evaluate`, `EvaluateWithEnvelope`, etc.
- `Curve` — 1D x/y data: linear interpolation, polynomial/Gaussian/
  Savitzky-Golay fitting, filtering.
- `Image` — ~250 bound methods. FFTW-backed real/complex numpy-backed
  arrays: `Allocate`, `ForwardFFT`/`BackwardFFT`, `ExtractSlice` (3D→2D
  Fourier slice extraction), `ApplyCTF`, `SwapRealSpaceQuadrants`,
  masking/filtering/normalization, MRC file I/O. This is the hard part —
  needs bit-for-bit (or numerically close) parity with cisTEM's specific
  FFTW padding/addressing/quadrant-swap conventions.

Not started. Will need its own sub-inventory of which of the ~250 `Image`
methods are actually exercised (start from `tests/test_core.py` +
`examples/test_extract_slice.py`: `Allocate`, `ForwardFFT`, `BackwardFFT`,
`ZeroCentralPixel`, `SwapRealSpaceQuadrants`, `ExtractSlice`, `ApplyCTF`,
`QuickAndDirtyWriteSlice`, `real_values`).

### Unused anywhere outside `pycistem/core/` — skip

All `*Asset`/`*AssetList` classes (`Asset`, `MovieAsset`,
`MovieMetadataAsset`, `ImageAsset`, `ParticlePositionAsset`, `VolumeAsset`,
`AtomicCoordinatesAsset`, and their `*List` counterparts), `ElectronDose`,
`GetMRCDetails()`.

## Testing approach

`tests/pycore/` mirrors this package. Each test does
`pytest.importorskip("pycistem.core")` up front, then constructs both the
compiled-core object and the pycore object with the same inputs and
asserts equivalent behavior/output (`pytest.approx` for floats). This lets
the suite run fully in CI/dev environments without the C++ toolchain
(tests just get skipped) while still giving real parity coverage when the
compiled extension is available (e.g. the `pycistem` conda env used during
development, see `/groups/elferich/.conda/envs/pycistem`).

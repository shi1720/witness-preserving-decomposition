"""Collect a NEW snapshot; live downloads do not reproduce an old registry state."""
import datetime,hashlib,json,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
packages='numpy scipy pandas torch tensorflow jaxlib onnxruntime tokenizers lxml pydantic-core grpcio pyarrow opencv-python cryptography pillow scikit-learn psutil orjson uvloop greenlet cffi aiohttp ml-dtypes h5py sentencepiece safetensors xgboost lightgbm numba llvmlite'.split()
out=ROOT/'data/pypi';out.mkdir(parents=True,exist_ok=True);manifest=[]
for package in packages:
 url=f'https://pypi.org/pypi/{package}/json';data=urllib.request.urlopen(url,timeout=60).read()
 (out/(package+'.json')).write_bytes(data)
 manifest.append({'package':package,'url':url,'sha256':hashlib.sha256(data).hexdigest(),'collected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()})
(ROOT/'data/fetch_manifest.json').write_text(json.dumps(manifest,indent=2))

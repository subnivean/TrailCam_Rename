from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

# Set the root level for Trail Camera pictures:
ROOTDIR = "/home/mark/TrailCam"

# FIXME: This will change when we go between EDT/EST
TIMECHANGE = timedelta(hours=4)

# Anything this many seconds away from midnight gets
# put in the prior day's folder.
ROLLBACK = 12 * 3600

# Get a list of all the JPEGS, looking for different
# formats separately.
jpegs0 = list(Path(ROOTDIR).glob("**/*_.[Jj][Pp][Gg]"))
jpegs1 = list(Path(ROOTDIR).glob("**/DSC*.[Jj][Pp][Gg]"))

jpegs = jpegs0 + jpegs1

# Don't touch files in 'keepers'
jpegs = [f for f in jpegs if "keepers" not in f.as_posix().lower()]

jcnt = len(jpegs)

for n, jpeg in enumerate(jpegs[0:], 1):
    ts = jpeg.stat().st_mtime
    dts = datetime.fromtimestamp(ts)
    adts = dts + TIMECHANGE
    adts = adts.replace(tzinfo=ZoneInfo("America/New_York"))

    if bool(adts.dst()) is False:
        adts = adts + timedelta(hours=1)

    midnight = datetime.combine(adts.date(), datetime.min.time())
    midnight = midnight.replace(tzinfo=ZoneInfo("America/New_York"))

    daybefore = midnight - timedelta(days=1)
    dbfoldername = daybefore.strftime("%Y%m%d")
    tdfoldername = midnight.strftime("%Y%m%d")

    secsaftermidnight = (adts - midnight).total_seconds()
    folder = dbfoldername if secsaftermidnight < ROLLBACK else tdfoldername

    folderpath = Path(ROOTDIR) / folder[0:4] / folder

    if not folderpath.is_dir():
        folderpath.mkdir(parents=True)

    newname = adts.isoformat().replace("-", "_").replace(":", "_") + ".jpg"
    newpath = folderpath / newname

    print(f"{n} of {jcnt}")
    print(f"{jpeg=}")
    print(f"{newpath=}")

    jpeg.rename(newpath)

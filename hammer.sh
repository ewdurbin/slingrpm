
rm repos/foo/*.rpm
for f in `ls ~/rpms`; do
  python slingrpm/slinger.py http://localhost:8000/repos/foo/ ~/rpms/$f &
done


rm repos/foo/*.rpm
rm repos/foo/.slingrpmincoming/*.rpm
rm repos/bar/pkgs/*.rpm
rm repos/bar/pkgs/.slingrpmincoming/*.rpm
for f in `ls ~/rpms`; do
  python slingrpm/slinger.py http://localhost:8000/repos/foo/ ~/rpms/$f &
  python slingrpm/slinger.py http://localhost:8000/repos/bar/ ~/rpms/$f &
done

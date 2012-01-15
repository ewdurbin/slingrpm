import konira
from pushrpm import RPM
describe "pushing a rpm package to our centralized repo":

  it "throws an exception if you dont specify the repo":
    raises Exception: RPM()
  it "throws an exception if the specified repo is not an http location":
    raises Exception: pusher = RPM(targetrepo="foo/bar/bazz")
  it "throws an exception if the specified repo is not a yum repo":
    raises Exception: pusher = RPM(targetrepo="http://localhost:8000/foo")
  it "likes repos with a repmod":
    pusher = RPM("http://localhost:8000/")
    assert pusher

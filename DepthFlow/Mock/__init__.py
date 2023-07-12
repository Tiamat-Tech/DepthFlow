
# Test timeline
if os.environ.get("TEST_TIMELINE", None):
    import DepthFlow.Mock.Timeline
    DepthFlow.Mock.Timeline.test_timeline()
    exit()

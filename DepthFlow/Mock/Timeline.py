from DepthFlow import *


def test_timeline():

    class CustomKeyframeA(BrokenKeyframe):
        def __call__(self, variables, T, t, tau):
            variables.A = Interpolation.lerp(a=0, b=1, t=t)
            variables.B = Interpolation.smoothstep(a=0, b=1, t=t)
            variables.C = Interpolation.heaviside(0.4, 0.6, t)

    class CustomKeyframeB(BrokenKeyframe):
        def __call__(self, variables, T, t, tau):
            variables.D = Continuous.triangle(tau, frequency=2, amplitude=0.5)

    # Create Timeline
    timeline = BrokenTimeline()

    # Add keyframes
    timeline.add_keyframe( CustomKeyframeA() @ (0.0, 1.0) )
    timeline.add_keyframe( CustomKeyframeB() @ 0.0 )

    # Import plotly
    import plotly.graph_objects as go

    # Axis
    X = linspace(0, 1, 1001)
    Y = dict()

    for T in X:
        success(f"• Time: {T:.2f}s", )
        variables = timeline.at(T)

        for key, value in variables.items():
            info(f"├─ {key.ljust(20)} = {value}")
            Y.setdefault(key, []).append(value)

    # Create plot
    fig = go.Figure()
    for key, value in Y.items():
        fig.add_trace(go.Scatter(x=X, y=value, name=key))
    fig.show()

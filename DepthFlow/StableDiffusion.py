
def mse_image(A: PilImage, B: PilImage) -> float:
    """
    Calculate the mean squared error between two images.
    """
    return numpy.square(numpy.subtract(A, B)).mean()

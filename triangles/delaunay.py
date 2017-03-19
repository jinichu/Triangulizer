#!/usr/bin/env python2
from __future__ import print_function
import sys

# Detect python version before continuing
if sys.version_info[0] == 3:
    print("delaunay.py only runs on Python 2.x")
    sys.exit(78)

import argparse
from PIL import Image, ImageDraw
from random import randrange
from collections import namedtuple
from math import sqrt
from geometry import delaunay_triangulation, tri_centroid, Point, Triangle
from distributions import *

# Some types to make things a little easier
Color = namedtuple('Color', 'r g b')
Gradient = namedtuple('Gradient', 'start end')


def hex_to_color(hex_value):
    """
    Convert a hexadecimal representation of a color to an RGB triplet.
    For example, the hex value FFFFFF corresponds to (255, 255, 255).
    Arguments:
    hex_value is a string containing a 6-digit hexadecimal color
    Returns:
    A Color object equivalent to the given hex value or None for invalid input
    """
    if hex_value is None:
        return None

    if hex_value[0] == '#':
        hex_value = hex_value[1:]

    hex_value = hex_value.lower()

    red = hex_value[:2]
    green = hex_value[2:4]
    blue = hex_value[4:]

    try:
        return Color(int(red, 16), int(green, 16), int(blue, 16))
    except ValueError:
        return None


def cart_to_screen(points, size):
    """
    Convert Cartesian coordinates to screen coordinates.
    Arguments:
    points is a list of Point objects or a vertex-defined Triangle object
    size is a 2-tuple of the screen dimensions (width, height)
    Returns:
    A list of Point objects or a Triangle object, depending on the type of the input
    """
    if isinstance(points, Triangle):
        return Triangle(
            Point(points.a.x, size[1] - points.a.y),
            Point(points.b.x, size[1] - points.b.y),
            Point(points.c.x, size[1] - points.c.y)
        )
    else:
        trans_points = [Point(p.x, size[1] - p.y) for p in points]
        return trans_points


def calculate_color(grad, val):
    """
    Calculate a point on a color gradient. Color values are in [0, 255].
    Arguments:
    grad is a Gradient object
    val is a value in [0, 1] indicating where the color is on the gradient
    Returns:
    A Color object
    """
    slope_r = grad.end.r - grad.start.r
    slope_g = grad.end.g - grad.start.g
    slope_b = grad.end.b - grad.start.b

    r = int(grad.start.r + slope_r*val)
    g = int(grad.start.g + slope_g*val)
    b = int(grad.start.b + slope_b*val)

    # Perform thresholding
    r = min(max(r, 0), 255)
    g = min(max(g, 0), 255)
    b = min(max(b, 0), 255)

    return Color(r, g, b)


def draw_polys(draw, colors, polys):
    """
    Draw a set of polygons to the screen using the given colors.
    Arguments:
    colors is a list of Color objects, one per polygon
    polys is a list of polygons defined by their vertices as x, y coordinates
    """
    for i in range(0, len(polys)):
        draw.polygon(polys[i], fill=colors[i])


def draw_lines(draw, color, polys, line_thickness=1):
    """
    Draw the edges of the given polygons to the screen in the given color.
    Arguments:
    draw is an ImageDraw object
    color is a Color tuple
    polys is a list of vertices
    line_thickness is the thickness of each line in px (default 1)
    """
    if line_thickness is None:
        line_thickness = 1

    for p in polys:
        draw.line(p, color, line_thickness)


def draw_points(draw, color, polys, vert_radius=16):
    """
    Draw the vertices of the given polygons to the screen in the given color.
    Arguments:
    draw is an ImageDraw object
    color is a Color tuple
    polys is a list of vertices
    vert_radius is the radius of each vertex in px (default 16)
    """
    if vert_radius is None:
        vert_radius = 16

    for p in polys:
        v1 = [p[0].x - vert_radius/2, p[0].y - vert_radius/2, p[0].x + vert_radius/2, p[0].y + vert_radius/2]
        v2 = [p[1].x - vert_radius/2, p[1].y - vert_radius/2, p[1].x + vert_radius/2, p[1].y + vert_radius/2]
        v3 = [p[2].x - vert_radius/2, p[2].y - vert_radius/2, p[2].x + vert_radius/2, p[2].y + vert_radius/2]
        draw.ellipse(v1, color)
        draw.ellipse(v2, color)
        draw.ellipse(v3, color)


def color_from_image(background_image, triangles):
    """
    Color a graph of triangles using the colors from an image.
    The color of each triangle is determined by the color of the image pixel at
    its centroid.
    Arguments:
    background_image is a PIL Image object
    triangles is a list of vertex-defined Triangle objects
    Returns:
    A list of Color objects, one per triangle such that colors[i] is the color
    of triangle[i]
    """
    colors = []
    pixels = background_image.load()
    size = background_image.size
    for t in triangles:
        centroid = tri_centroid(t)
        # Truncate the coordinates to fit within the boundaries of the image
        int_centroid = (
            int(min(max(centroid[0], 0), size[0]-1)),
            int(min(max(centroid[1], 0), size[1]-1))
        )
        # Get the color of the image at the centroid
        p = pixels[int_centroid[0], int_centroid[1]]
        colors.append(Color(p[0], p[1], p[2]))
    return colors


def color_from_gradient(gradient, image_size, triangles):
    """
    Color a graph of triangles using a gradient.
    Arguments:
    gradient is a Gradient object
    image_size is a tuple of the output dimensions, i.e. (width, height)
    triangles is a list of vertex-defined Triangle objects
    Returns:
    A list of Color objects, one per triangle such that colors[i] is the color
    of triangle[i]
    """
    colors = []
    # The size of the screen
    s = sqrt(image_size[0]**2+image_size[1]**2)
    for t in triangles:
        # The color is determined by the location of the centroid
        tc = tri_centroid(t)
        # Bound centroid to boundaries of the image
        c = (min(max(0, tc[0]), image_size[0]),
             min(max(0, tc[1]), image_size[1]))
        frac = sqrt(c[0]**2+c[1]**2)/s
        colors.append(calculate_color(gradient, frac))
    return colors


def triangularize(input_filename, npoints):
    """Calculate Delaunay triangulation and output an image"""
    aa_amount = 4
    output_filename = "triangle_" + input_filename
    aa_amount = 4
    background_image = Image.open(input_filename)
    size = background_image.size

    # Generate points on this portion of the canvas
    scale = 1.25
    points = generate_random_points(npoints, size, scale, False)

    # Dedup the points
    points = list(set(points))

    # Calculate the triangulation
    triangulation = delaunay_triangulation(points)

    # Failed to find a triangulation
    if not triangulation:
        print('Failed to find a triangulation.')
        return None

    # Translate the points to screen coordinates
    trans_triangulation = list(map(lambda x: cart_to_screen(x, size), triangulation))

    # Assign colors to the triangles
    colors = color_from_image(background_image, trans_triangulation)

    # Create image object
    image = Image.new('RGB', size, 'white')
    # Get a draw object
    draw = ImageDraw.Draw(image)
    # Draw the triangulation
    draw_polys(draw, colors, trans_triangulation)

    # Write the image to a file
    image.save(output_filename)
    print('Image saved to %s' % output_filename)
    return output_filename

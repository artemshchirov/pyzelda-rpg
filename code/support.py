import os
import pygame
from csv import reader


def import_csv_layout(path: str) -> list:
    terrain_map = []
    with open(path) as level_map:
        layout = reader(level_map, delimiter=',')
        for row in layout:
            terrain_map.append(list(row))
        return terrain_map


def import_folder(path: str) -> list:
    surface_list = []

    for _, __, img_files in os.walk(path):
        for image in img_files:
            full_path = path + '/' + image
            image_surf = pygame.image.load(full_path).convert_alpha()
            surface_list.append(image_surf)

    return surface_list


def get_path(path):
    absolute_path = os.path.dirname(__file__)
    full_path = os.path.join(absolute_path, path)

    return full_path

import pygame


def _is_audio_enabled():
    try:
        import settings
    except ModuleNotFoundError:
        return True
    return getattr(settings, 'IS_MUSIC_ENABLED', True)


def play_sound(sound, loops=0):
    if sound and _is_audio_enabled():
        try:
            sound.play(loops)
        except pygame.error:
            pass


def stop_sound(sound):
    if sound:
        try:
            sound.stop()
        except pygame.error:
            pass


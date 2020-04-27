import pygame
from render import render_wait_screen


def key_handler(state, event):
    if event.key == pygame.K_RETURN:
        wait_screen = render_wait_screen(state.render_parameters)
        display_update(
            state,
            state.screen,
            wait_screen,
            [state.screen_width, state.screen_height],
            state.render_parameters.scroll_x,
            state.render_parameters.scroll_y)
        state.city.gen_random_pts()
        state.city.get_edge_regions()

        state.city.relax_points()
        state.city.generate_structures(state.gen_parameters)
    elif event.key == pygame.K_EQUALS:

        state.render_parameters.margin += 5
        state.render_parameters.margin = min(
            state.render_parameters.margin,
            state.screen_width,
            state.screen_height)
    elif event.key == pygame.K_MINUS:
        state.render_parameters.margin -= 5
        state.render_parameters.margin = max(
            state.render_parameters.margin,
            0)
    elif event.key == pygame.K_m:
        state.render_parameters.toggle_mesh_mode()
    elif event.key == pygame.K_PERIOD:
        state.render_parameters.zoom += 0.05
    elif event.key == pygame.K_COMMA:
        state.render_parameters.zoom -= 0.05
        state.render_parameters.zoom = max(state.render_parameters.zoom, 0.05)
    elif event.key == pygame.K_LEFT:
        state.render_parameters.scroll_x += 10
        return
    elif event.key == pygame.K_RIGHT:
        state.render_parameters.scroll_x -= 10
        return
    elif event.key == pygame.K_UP:
        state.render_parameters.scroll_y += 10
        return
    elif event.key == pygame.K_DOWN:
        state.render_parameters.scroll_y -= 10
        return
    elif event.key == pygame.K_r:
        state.render_parameters.scroll_y = 0
        state.render_parameters.scroll_x = 0
        state.render_parameters.zoom = 1.0
    else:
        print(pygame.key.name(event.key))
        return
    state.city_map_image = render_image(
        state.city,
        state.render_parameters)


def mousedown_handler(state, event):
    left_click = pygame.mouse.get_pressed()[0]
    if left_click:
        print("event!")
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_adj = (mouse_pos[0] - state.render_parameters.scroll_x, mouse_pos[1] - state.render_parameters.scroll_y)
        state.mouse_down = True
        state.drag_start = mouse_pos_adj


def mouseup_handler(state, event):
    state.mouse_down = False
    state.drag_start = ()


def input_handler(event):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.display.quit()
            pygame.quit()
        if event.type == pygame.KEYDOWN:
            key_handler(state, event)

        if event.type == pygame.MOUSEBUTTONDOWN:
            mousedown_handler(state, event)

        if event.type == pygame.MOUSEBUTTONUP:
            mouseup_handler(state, event)


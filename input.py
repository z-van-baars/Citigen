import pygame
import render as rdr


def key_handler(state, event):
    if event.key == pygame.K_RETURN:
        state.cached_image = rdr.render_message_screen(
            [state.screen_width, state.screen_height],
            "Regenerating...")
        rdr.display_update(
            state,
            state.screen,
            [state.screen_width, state.screen_height],
            state.render_parameters.scroll_x,
            state.render_parameters.scroll_y)

        state.city.initalize_blank_map()
        state.city.gen_random_pts()
        state.city.get_edge_regions()

        state.city.relax_points()
        state.city.generate_structures(state.gen_parameters)
        state.max_lod_image = rdr.render_image(
            state.city,
            state.render_parameters)
        state.cached_image = rdr.rescale_map_image(
            state.max_lod_image,
            state.max_lod_image.get_width(),
            state.render_parameters.scale)
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
        state.render_parameters.scale += 0.05
    elif event.key == pygame.K_COMMA:
        state.render_parameters.scale -= 0.05
        state.render_parameters.scale = max(state.render_parameters.scale, 0.05)
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
        state.render_parameters.scale = 0.4
    else:
        print(pygame.key.name(event.key))
        return
    state.max_lod_image = rdr.render_image(
        state.city,
        state.render_parameters)


def mousedown_handler(state, event):
    if event.button == 1:
        mouse_pos = pygame.mouse.get_pos()
        mouse_pos_adj = (
            mouse_pos[0] - state.render_parameters.scroll_x,
            mouse_pos[1] - state.render_parameters.scroll_y)
        state.mouse_down = True
        state.drag_start = mouse_pos_adj
    if event.button == 4:
        state.render_parameters.scale += 0.02
        state.cached_image = rdr.rescale_map_image(
            state.max_lod_image,
            state.max_lod_image.get_width(),
            state.render_parameters.scale)
    if event.button == 5:
        state.render_parameters.scale -= 0.02
        state.cached_image = rdr.rescale_map_image(
            state.max_lod_image,
            state.max_lod_image.get_width(),
            state.render_parameters.scale)


def mouseup_handler(state, event):
    state.mouse_down = False
    state.drag_start = ()


def input_handler(state):
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


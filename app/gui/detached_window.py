import queue
import threading
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer


class DetachedWindow:
    def __init__(self, title="Detached Window", width=400, height=300):
        self.title = title
        self.width = width
        self.height = height
        self.thread = None
        self.running = False
        self.created = False
        self.window_closed = False
        self.queue = queue.Queue()
        self.window = None
        self.context = None
        self.impl = None

        self.render_func = None

    def _window_refresh_callback(self, window):
        pass

    def _framebuffer_size_callback(self, window, width, height):
        self.width = width
        self.height = height
    def start(self):
        if self.created:
            return
        self.created = True
        self.running = True
        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        glfw.set_window_refresh_callback(self.window, self._window_refresh_callback)
        glfw.set_window_size_callback(self.window, self._framebuffer_size_callback)
        self.thread = threading.Thread(target=self._run)
        self.thread.start()

    def stop(self):
        if not self.created:
            return
        self.created = False
        self.running = False
        self.window_closed = False
        self.thread.join()
        glfw.destroy_window(self.window)

    def update(self):
        if self.running and self.window_closed:
            self.stop()

    def _run(self):

        glfw.make_context_current(self.window)
        self.context = imgui.create_context()
        imgui.set_current_context(self.context)
        self.impl = GlfwRenderer(self.window)
        self.running = True

        while not glfw.window_should_close(self.window) and self.running:
            if self.render_func is not None:
                self._render_2()

            glfw.swap_buffers(self.window)
        self.window_closed = True
        self.impl.shutdown()
        imgui.destroy_context(self.context)

    def _render_2(self):
        imgui.set_current_context(self.context)
        self.impl.process_inputs()
        imgui.new_frame()

        self.render_func()

        # imgui.end()
        imgui.render()
        self.impl.render(imgui.get_draw_data())

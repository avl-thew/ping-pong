from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty, OptionProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle, Line
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from random import choice, uniform
import os

# Регистрируем шрифт
LabelBase.register(name='GameFont', fn_regular='/usr/share/fonts/dejavu-sans-fonts/DejaVuSans.ttf')

class PongPaddle(Widget):
    score = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.is_player1 = True
        
    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            if self.is_player1:
                Color(1, 0.55, 0.8, 1)
            else:
                Color(1, 0.25, 0.6, 1)
            
            RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
            
            Color(1, 1, 1, 0.9)
            for i in range(3):
                y_pos = self.y + 20 + i * (self.height - 40) / 2
                Ellipse(pos=(self.x + self.width/2 - 4, y_pos - 4), size=(8, 8))

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.15
            ball.velocity = vel.x, vel.y + offset * 3
            ball.velocity_y += uniform(-1, 1)

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas)
        
    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(1, 0.6, 0.9, 0.4)
            Ellipse(pos=(self.x - 15, self.y - 15), size=(self.width + 30, self.height + 30))
            
            Color(1, 1, 1, 1)
            Ellipse(pos=self.pos, size=self.size)
            
            Color(1, 0.4, 0.7, 1)
            bow_center_x = self.center_x
            bow_center_y = self.center_y + self.height/4
            Ellipse(pos=(bow_center_x - 12, bow_center_y - 6), size=(12, 12))
            Ellipse(pos=(bow_center_x, bow_center_y - 6), size=(12, 12))
            Ellipse(pos=(bow_center_x - 4, bow_center_y - 4), size=(8, 8))

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos

class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    ai_mode = True
    
    # Только 'local' или 'drawn' - без интернета!
    bg_mode = OptionProperty('drawn', options=['local', 'drawn'])
    bg_texture = ObjectProperty(None, allownone=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.draw_background, pos=self.draw_background)
        self.setup_background()
        
    def setup_background(self):
        """Настройка фона"""
        if self.bg_mode == 'local':
            # Проверяем несколько возможных имён файла
            possible_names = [
                'hello_kitty_bg.jpg',
                'bg.png',
                'background.png',
                'kitty.jpg',
                'hello_kitty.jpg'
            ]
            
            found = False
            for filename in possible_names:
                if os.path.exists(filename):
                    try:
                        self.bg_texture = CoreImage(filename).texture
                        print(f"Загружена картинка: {filename}")
                        found = True
                        break
                    except Exception as e:
                        print(f"Ошибка загрузки {filename}: {e}")
                        continue
            
            if not found:
                print("Картинка не найдена, переключаюсь на режим 'drawn'")
                self.bg_mode = 'drawn'
        
    def draw_hello_kitty_pattern(self):
        """Рисуем Hello Kitty и узоры сами"""
        # Рисуем несколько Hello Kitty по углам
        positions = [
            (self.x + 30, self.y + 30, 70),       # Низ слева
            (self.right - 100, self.y + 30, 70),   # Низ справа
            (self.x + 30, self.top - 100, 70),     # Верх слева
            (self.right - 100, self.top - 100, 70) # Верх справа
        ]
        
        for x, y, size in positions:
            self.draw_hello_kitty(x, y, size)
            
        # Добавляем сердечки по всему фону
        heart_positions = [
            (self.center_x - 150, self.center_y + 100),
            (self.center_x + 150, self.center_y + 100),
            (self.center_x - 150, self.center_y - 100),
            (self.center_x + 150, self.center_y - 100),
            (self.center_x, self.center_y + 150),
            (self.center_x, self.center_y - 150),
        ]
        
        for hx, hy in heart_positions:
            self.draw_heart(hx, hy, 25)
        
    def draw_hello_kitty(self, x, y, size):
        """Рисует упрощенную Hello Kitty"""
        s = size
        
        # Ушки (розовые овалы)
        Color(1, 0.7, 0.85, 0.7)
        Ellipse(pos=(x + s*0.1, y + s*0.75), size=(s*0.35, s*0.4))
        Ellipse(pos=(x + s*0.55, y + s*0.75), size=(s*0.35, s*0.4))
        
        # Голова (белый круг)
        Color(1, 1, 1, 0.9)
        Ellipse(pos=(x + s*0.1, y + s*0.2), size=(s*0.8, s*0.7))
        
        # Глаза (черные овалы)
        Color(0.2, 0.1, 0.1, 0.9)
        Ellipse(pos=(x + s*0.3, y + s*0.45), size=(s*0.08, s*0.12))
        Ellipse(pos=(x + s*0.62, y + s*0.45), size=(s*0.08, s*0.12))
        
        # Нос (желтый овал)
        Color(1, 0.9, 0.3, 0.9)
        Ellipse(pos=(x + s*0.46, y + s*0.38), size=(s*0.08, s*0.06))
        
        # Усы (черные линии)
        Color(0.2, 0.1, 0.1, 0.8)
        # Левые усы
        Line(points=[x + s*0.15, y + s*0.5, x + s*0.05, y + s*0.55], width=2)
        Line(points=[x + s*0.15, y + s*0.45, x + s*0.05, y + s*0.45], width=2)
        Line(points=[x + s*0.15, y + s*0.4, x + s*0.05, y + s*0.35], width=2)
        # Правые усы
        Line(points=[x + s*0.85, y + s*0.5, x + s*0.95, y + s*0.55], width=2)
        Line(points=[x + s*0.85, y + s*0.45, x + s*0.95, y + s*0.45], width=2)
        Line(points=[x + s*0.85, y + s*0.4, x + s*0.95, y + s*0.35], width=2)
        
        # Бантик (розовый с белым центром)
        Color(1, 0.4, 0.6, 0.95)
        bow_x = x + s*0.65
        bow_y = y + s*0.75
        # Левая часть банта
        Ellipse(pos=(bow_x - s*0.15, bow_y - s*0.1), size=(s*0.2, s*0.25))
        # Правая часть банта
        Ellipse(pos=(bow_x + s*0.05, bow_y - s*0.1), size=(s*0.2, s*0.25))
        # Центр банта
        Color(1, 1, 1, 0.95)
        Ellipse(pos=(bow_x - s*0.05, bow_y - s*0.05), size=(s*0.15, s*0.15))
        
    def draw_heart(self, x, y, size):
        """Рисует сердечко"""
        Color(1, 0.5, 0.7, 0.5)
        # Два перекрывающихся круга = сердечко
        Ellipse(pos=(x - size*0.5, y), size=(size, size*0.9))
        Ellipse(pos=(x, y), size=(size, size*0.9))
        
    def draw_background(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            if self.bg_mode == 'local' and self.bg_texture:
                # Локальная картинка
                Color(1, 1, 1, 0.6)
                Rectangle(pos=self.pos, size=self.size, texture=self.bg_texture)
            else:
                # Рисуем сами
                Color(1, 0.9, 0.95, 1)
                Rectangle(pos=self.pos, size=self.size)
                self.draw_hello_kitty_pattern()
            
            # Декоративные полоски по краям
            Color(1, 0.6, 0.8, 0.7)
            Rectangle(pos=(self.x, self.y), size=(25, self.height))
            Rectangle(pos=(self.right - 25, self.y), size=(25, self.height))

    def serve_ball(self, vel=(5, 0)):
        self.ball.center = self.center
        direction_x = choice([-1, 1])
        self.ball.velocity = (vel[0] * direction_x, uniform(-3, 3))

    def update(self, dt):
        self.ball.move()
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        if self.ball.y < self.y:
            self.ball.y = self.y
            self.ball.velocity_y *= -0.95
        if self.ball.top > self.top:
            self.ball.top = self.top
            self.ball.velocity_y *= -0.95

        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(5, 0))
        if self.ball.right > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(5, 0))

        if self.ai_mode:
            self.ai_move_paddle(dt)

    def ai_move_paddle(self, dt):
        if self.ball.velocity_x > 0:
            target_y = self.ball.center_y
        else:
            target_y = self.center_y
        
        target_y = max(self.player2.height/2, min(self.height - self.player2.height/2, target_y))
        current_y = self.player2.center_y
        diff = target_y - current_y
        speed = 800 * dt
        
        if abs(diff) < speed:
            self.player2.center_y = target_y
        elif diff > 0:
            self.player2.center_y += speed
        else:
            self.player2.center_y -= speed

    def on_touch_down(self, touch):
        if touch.is_double_tap:
            self.ai_mode = not self.ai_mode
            self.serve_ball()
        # Тройной клик для смены фона
        if touch.is_triple_tap:
            modes = ['local', 'drawn']
            current_idx = modes.index(self.bg_mode)
            self.bg_mode = modes[(current_idx + 1) % len(modes)]
            self.setup_background()
            self.draw_background()
            print(f"Режим фона: {self.bg_mode}")
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.x < self.width / 2:
            self.player1.center_y = touch.y
        elif not self.ai_mode and touch.x > self.width / 2:
            self.player2.center_y = touch.y

class PongApp(App):
    def build(self):
        self.title = "Hello Kitty Pong"
        Window.clearcolor = (1, 0.94, 0.96, 1)
        
        game = PongGame()
        game.player1.is_player1 = True
        game.player2.is_player1 = False
        game.player1.update_canvas()
        game.player2.update_canvas()
        
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ == '__main__':
    PongApp().run()
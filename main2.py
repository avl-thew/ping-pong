from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ReferenceListProperty, ObjectProperty
from kivy.vector import Vector
from kivy.clock import Clock
from kivy.graphics import Color, Ellipse, Rectangle, RoundedRectangle
from kivy.core.text import Label as CoreLabel
from random import choice, uniform

class PongPaddle(Widget):
    score = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        self.is_player1 = True  # Определяем цвет ракетки
        
    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Градиентный эффект для ракетки
            if self.is_player1:
                Color(1, 0.55, 0.8, 1)  # Розовая для игрока 1
            else:
                Color(1, 0.25, 0.6, 1)   # Малиновая для игрока 2
            
            RoundedRectangle(pos=self.pos, size=self.size, radius=[15])
            
            # Белые полоски (как у Hello Kitty)
            Color(1, 1, 1, 0.9)
            for i in range(3):
                y_pos = self.y + 20 + i * (self.height - 40) / 2
                Ellipse(pos=(self.x + self.width/2 - 4, y_pos - 4), size=(8, 8))

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.15  # Чуть быстрее
            ball.velocity = vel.x, vel.y + offset * 3  # Больше углов!
            
            # Добавляем случайность для интереса
            ball.velocity_y += uniform(-1, 1)

class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(pos=self.update_canvas)
        self.rotation = 0
        
    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Свечение вокруг мяча
            Color(1, 0.6, 0.9, 0.4)
            Ellipse(pos=(self.x - 15, self.y - 15), size=(self.width + 30, self.height + 30))
            
            # Основной мяч (белый с розовым бантиком)
            Color(1, 1, 1, 1)
            Ellipse(pos=self.pos, size=self.size)
            
            # Розовый бантик на мяче
            Color(1, 0.4, 0.7, 1)
            bow_center_x = self.center_x
            bow_center_y = self.center_y + self.height/4
            # Левая часть банта
            Ellipse(pos=(bow_center_x - 12, bow_center_y - 6), size=(12, 12))
            # Правая часть банта
            Ellipse(pos=(bow_center_x, bow_center_y - 6), size=(12, 12))
            # Центр банта
            Ellipse(pos=(bow_center_x - 4, bow_center_y - 4), size=(8, 8))

    def move(self):
        self.pos = Vector(*self.velocity) + self.pos
        self.rotation += 5

class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)
    ai_mode = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self.draw_background, pos=self.draw_background)
        
    def draw_background(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            # Фон с сердечками-узором (упрощенный)
            Color(1, 0.94, 0.96, 1)  # Нежно-розовый фон
            Rectangle(pos=self.pos, size=self.size)
            
            # Декоративные полоски по краям
            Color(1, 0.7, 0.85, 0.5)
            Rectangle(pos=(self.x, self.y), size=(20, self.height))
            Rectangle(pos=(self.right - 20, self.y), size=(20, self.height))

    def serve_ball(self, vel=(5, 0)):
        self.ball.center = self.center
        direction_x = choice([-1, 1])
        self.ball.velocity = (vel[0] * direction_x, uniform(-3, 3))

    def update(self, dt):
        self.ball.move()

        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # Отскок от стенок с эффектом
        if self.ball.y < self.y:
            self.ball.y = self.y
            self.ball.velocity_y *= -0.95
        if self.ball.top > self.top:
            self.ball.top = self.top
            self.ball.velocity_y *= -0.95

        # Счет
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(5, 0))
        if self.ball.right > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(5, 0))

        if self.ai_mode:
            self.ai_move_paddle(dt)

    def ai_move_paddle(self, dt):
        # Улучшенный ИИ с небольшой задержкой для честности
        if self.ball.velocity_x > 0:
            target_y = self.ball.center_y + (self.ball.velocity_y * 0.1)
        else:
            target_y = self.center_y
        
        target_y = max(self.player2.height/2, min(self.height - self.player2.height/2, target_y))
        
        current_y = self.player2.center_y
        diff = target_y - current_y
        speed = 500 * dt  # Чуть медленнее, чтобы можно было выиграть
        
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
        return super().on_touch_down(touch)

    def on_touch_move(self, touch):
        if touch.x < self.width / 2:
            self.player1.center_y = touch.y
        elif not self.ai_mode and touch.x > self.width / 2:
            self.player2.center_y = touch.y

class PongApp(App):
    def build(self):
        self.title = "Hello Kitty Pong 💕"
        
        # Настройка окна
        from kivy.core.window import Window
        Window.clearcolor = (1, 0.94, 0.96, 1)
        
        game = PongGame()
        
        # Настройка ракеток после создания
        game.player1.is_player1 = True
        game.player2.is_player1 = False
        game.player1.update_canvas()
        game.player2.update_canvas()
        
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ == '__main__':
    PongApp().run()
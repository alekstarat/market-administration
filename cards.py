from flet import (
    flet,
    Page,
    UserControl,
    Container,
    animation,
    border,
    alignment,
    Text,
    Column,
    Row,
    colors,
    Card,
    transform,
    ElevatedButton,
    IconButton
)
import flet as ft
from datetime import datetime
from database import Base
import time
from CONFIG import *


def from_unix(time):
    return datetime.utcfromtimestamp(time).strftime('%d-%m-%Y')

class AnimatedCard(UserControl):
    def __init__(self, operation_id, user_id, position_id, TIME):
        # List : ['Podonki', 'БананМанго', '400', '3']

        self.base = Base(BASE)
        self.operation_id = operation_id
        self.user_id = user_id
        self.position_id = position_id
        d = list(self.base.cur.execute(f"SELECT name, type FROM Liquids WHERE id = {position_id}"))[0]
        self.username = list(self.base.cur.execute(f'SELECT username FROM TelegramUsers WHERE id = {self.user_id}'))[0][0]
        self.base.con.close()
        self.NAME = d[0]
        self.TYPE = d[1]
        
        self.TIME = from_unix(TIME)
        super().__init__()

    def build(self):
        def on_click(e):
            
            base = Base(BASE)
            if list(base.cur.execute(f"SELECT reservationCount FROM TelegramUsers WHERE id = {self.user_id}"))[0][0] > 0:
                base.cur.execute(f"UPDATE TelegramUsers SET reservationCount = reservationCount - 1 WHERE id = {self.user_id}")
                base.cur.execute(f"INSERT INTO Transactions VALUES ({self.operation_id}, {self.user_id}, {self.position_id}, {int(time.time())}, {list(base.cur.execute(f'SELECT price FROM Liquids WHERE id = {self.position_id}'))[0][0]})")
                base.cur.execute(f"DELETE FROM Reservation WHERE operationID = {self.operation_id}")
                base.con.commit()
                base.con.close()
                print('Продано!')
                self.page.clean()
                self.page.update()
            else:
                print('Забагал нахуй таблицу')
            
            
        self._icon_container_ = Container(
            width=200,
            height=100,
            bgcolor=colors.BLUE_800,
            border_radius=25,
            animate_opacity=200,
            offset=transform.Offset(0, 0.25),
            animate_offset=animation.Animation(duration=900, curve="ease"),
            visible=False,
            content=Row(
                alignment="center",
                vertical_alignment="center",
                controls=[
                    IconButton(icon=ft.icons.CHECK_BOX, bgcolor=ft.colors.GREEN_800, on_click=on_click)
                    
                    
                ],
            ),
        )

        self._container = Container(
            width=280,
            height=380,
            bgcolor=colors.BLUE_GREY_800,
            border_radius=12,
            on_hover=lambda e: self.AnimatedCardHover(e),
            animate=animation.Animation(600, "ease"),
            border=border.all(2, colors.WHITE24),
            content=Column(
                alignment="center",
                horizontal_alignment="start",
                spacing=0,
                controls=[
                    Container(
                        padding=20,
                        alignment=alignment.center,
                        content=Text(
                            f"{self.NAME} {self.TYPE}",
                            color=colors.BLACK,
                            size=28,
                            weight="w800",
                        ),
                    ),
                    Container(
                        padding=20,
                        alignment=alignment.top_center,
                        content=Text(
                            f"для @{self.username}",
                            color=colors.BLACK,
                            size=14,
                            weight="w500",
                        ),
                    ),
                    Container(
                        padding=20,
                        alignment=alignment.bottom_center,
                        content=Text(
                            f'до {self.TIME}',
                            color=colors.BLACK,
                            size=14,
                            weight="w300"
                        )
                    )
                ],
            ),
        )

        self.__card = Card(
            elevation=0,
            content=Container(
                content=Column(
                    spacing=0,
                    horizontal_alignment="center",
                    controls=[
                        self._container,
                    ],
                ),
            ),
        )

        self._card = Column(
            horizontal_alignment="center",
            spacing=0,
            controls=[
                self.__card,
                self._icon_container_,
            ],
        )

        self._main = self._card

        return self._main

    def AnimatedCardHover(self, e):
        self._icon_container_.visible = True
        self._icon_container_.update()

        if e.data == "true":

            for __ in range(50):
                self.__card.elevation += 2
                self.__card.update()

            self._container.border = border.all(4, colors.BLUE_800)
            self._container.update()

            self._icon_container_.offset = transform.Offset(0, -0.75)
            self._icon_container_.opacity = 1
            self._icon_container_.update()

        else:
            for __ in range(50):
                self.__card.elevation -= 2
                self.__card.update()

            self._container.border = border.all(4, colors.WHITE24)
            self._container.update()

            self._icon_container_.offset = transform.Offset(0, 0.5)
            self._icon_container_.opacity = 0
            self._icon_container_.update()



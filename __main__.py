import flet as ft
from database import Base
from cal import FletCalendar
from cards import AnimatedCard
from datetime import datetime
import time

base = Base('C:/Users/Сашер/Desktop/base.sqlite')

def from_unix(time):
    return datetime.utcfromtimestamp(time).strftime('%d-%m-%Y')

def main(page: ft.Page):
    page.title = "Жижки у Насика"
    page.scroll = 'always'
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.update()

    def from_unix(time):
        return datetime.utcfromtimestamp(time).strftime('%d-%m-%Y')

    def get_data_from_sql(base: object, is_null: bool):
        if is_null:
            test_obj = base.cur.execute("SELECT * FROM Liquids")
        else:    
            test_obj = base.cur.execute("SELECT * FROM Liquids WHERE amount > 0")
        arr = []
        for i in test_obj:
            arr.append(list(i))
        del test_obj

        table = []
        for i in arr:
            temp = []
            for j in i:
                temp.append(ft.DataCell(ft.Text(str(j))))
            table.append(ft.DataRow(cells=temp, on_long_press=long_press))
        
        page.update()
        
        return table


    def long_press(e):
        id = e.control.cells[0].content.value
        amount = e.control.cells[-1].content.value
        BottomPanel(page, id, amount)

    def get_base_template():

        def bs_dismissed(e):
            print("Dismissed!")

        def show_bs(e):
            bs.open = True
            bs.update()

        def close_bs(e):
            bs.open = False
            if all([i.value for i in [brand_field, type_field, price_field, amount_field]]):
                base.cur.execute(f"INSERT INTO Liquids VALUES (NULL,'{brand_field.value}', '{type_field.value}', {int(price_field.value)}, {int(amount_field.value)})")
                base.con.commit()
                page.controls.clear()
                page.add(get_base_template())
                page.update()
            bs.update()

        brand_field = ft.TextField(suffix_text='Производитель')
        type_field = ft.TextField(suffix_text='Вкус')
        price_field = ft.TextField(suffix_text='Цена')
        amount_field = ft.TextField(suffix_text='Кол-во')

        bs = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        brand_field,
                        type_field,
                        price_field,
                        amount_field,
                        ft.ElevatedButton("Добавить", on_click=close_bs),
                    ],
                    tight=True,
                ),
                padding=10,
                width=840,
                height=600,
                alignment=ft.alignment.center
            ),
            open=False,
            on_dismiss=bs_dismissed,
        )
        page.overlay.append(bs)
        def template_object():
            base_template = ft.Container(
                        width=1280,
                        height=720,
                        content=ft.DataTable(columns=[
                            ft.DataColumn(ft.Text("ID")),
                            ft.DataColumn(ft.Text("Название")),
                            ft.DataColumn(ft.Text("Вкус")),
                            ft.DataColumn(ft.Text("Цена")),
                            ft.DataColumn(ft.Text("Кол-во")),
                        ],
                        rows=get_data_from_sql(base, True),)
                    )
            page.update()
            return base_template
        base_template = template_object()
        return ft.Column([ft.ElevatedButton('Добавить новый товар',on_click=show_bs, width=1280, height=50, bgcolor=ft.colors.GREEN_800),base_template])
    
    def BottomPanel(page: ft.Page, id, amount):
        page.vertical_alignment = ft.MainAxisAlignment.CENTER
        def bs_dismissed(e):
            print("Dismissed!")

        def show_bs(e):
            bs.open = True
            bs.update()


        def text_on_change(e):
            page.update()

        text = ft.TextField(value=f'{amount}', text_align=ft.TextAlign.RIGHT, on_change=text_on_change, width=100)
        
        def close_bs(e):
            
            bs.open = False
            print(text.value)
            base.cur.execute(f"UPDATE Liquids SET amount = {text.value} WHERE id = {id}")
            base.con.commit()
            page.controls.clear()
            page.add(get_base_template())
            bs.update()
            page.update()

        def increase(e):
            text.value = str(int(text.value) + 1)
            page.update()

        def decrease(e):
            text.value = str(int(text.value) - 1)
            page.update()

        def delete_elem(e):
            
            base.cur.execute(f"DELETE FROM Liquids WHERE id = {id}")
            base.con.commit()
            close_bs(e)

        inc_butt = ft.IconButton(icon=ft.icons.ARROW_LEFT, on_click=decrease)
        dec_butt = ft.IconButton(icon=ft.icons.ARROW_RIGHT, on_click=increase)
        del_button = ft.IconButton(icon=ft.icons.DELETE, bgcolor=ft.colors.RED_900, on_click=delete_elem)

        bs = ft.BottomSheet(
            ft.Container(
                ft.Column(
                    [
                        ft.Text(f"Редактировать кол-во: {id}"),
                        ft.Row([inc_butt, text, dec_butt, del_button]),
                        ft.ElevatedButton("Сохранить", on_click=close_bs),
                    ],
                    tight=True,
                    alignment=ft.alignment.center_right
                ),
                padding=10,
                width=700,
                height=200,
                alignment=ft.alignment.center_right
                
            ),
            open=True,
            on_dismiss=bs_dismissed,
            
        )
        page.overlay.append(bs)
        page.add(ft.ElevatedButton("Display bottom sheet", on_click=show_bs, visible=False))


    def get_date():
        return str(datetime.today().month)+ '-' + str(datetime.today().day) + '-' + str(datetime.today().year)
    
    task_date = ft.TextField(suffix_text='Дата', value=get_date())
    daily_task = ft.TextField(suffix_text='Заметка')

    def close_dlg(e: object):
            
        def save_task(date, text):
            with open(f'daily/{date}.txt', 'w', encoding='utf-8') as file:
                file.write(text)
                file.close()

        dlg.open = False
        save_task(task_date.value, daily_task.value)
        page.update()

    dlg = ft.AlertDialog(
        title=ft.Text('Добавление новой записи'), on_dismiss=close_dlg,
        content=ft.Column([task_date, daily_task, ft.ElevatedButton('Сохранить', on_click=close_dlg)])
    )

    def open_dlg(e):
        page.dialog = dlg
        dlg.open = True
        page.update()
    


    def change_content(e):

        page.controls.clear()
        nav_dest = e.control.selected_index

        if nav_dest == 0:
                
            class State:
                toggle = True

            s = State()

            chart_data_raw = list(base.cur.execute("SELECT * FROM Transactions"))
            bar_pos = list(set([i[2] for i in chart_data_raw]))
            print(bar_pos)
            print(chart_data_raw)

            data_0 = []

            data_1 = [
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(1, 1),
                        ft.LineChartDataPoint(3, 1.5),
                        ft.LineChartDataPoint(5, 1.4),
                        ft.LineChartDataPoint(7, 3.4),
                        ft.LineChartDataPoint(10, 2),
                        ft.LineChartDataPoint(12, 2.2),
                        ft.LineChartDataPoint(13, 1.8),
                    ],
                    stroke_width=8,
                    color=ft.colors.LIGHT_GREEN,
                    curved=True,
                    stroke_cap_round=True,
                ),
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(1, 1),
                        ft.LineChartDataPoint(3, 2.8),
                        ft.LineChartDataPoint(7, 1.2),
                        ft.LineChartDataPoint(10, 2.8),
                        ft.LineChartDataPoint(12, 2.6),
                        ft.LineChartDataPoint(13, 3.9),
                    ],
                    color=ft.colors.PINK,
                    below_line_bgcolor=ft.colors.with_opacity(0, ft.colors.PINK),
                    stroke_width=8,
                    curved=True,
                    stroke_cap_round=True,
                ),
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(1, 2.8),
                        ft.LineChartDataPoint(3, 1.9),
                        ft.LineChartDataPoint(6, 3),
                        ft.LineChartDataPoint(10, 1.3),
                        ft.LineChartDataPoint(13, 2.5),
                    ],
                    color=ft.colors.CYAN,
                    stroke_width=8,
                    curved=True,
                    stroke_cap_round=True,
                ),
            ]

            data_2 = [
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(1, 1),
                        ft.LineChartDataPoint(3, 4),
                        ft.LineChartDataPoint(5, 1.8),
                        ft.LineChartDataPoint(7, 5),
                        ft.LineChartDataPoint(10, 2),
                        ft.LineChartDataPoint(12, 2.2),
                        ft.LineChartDataPoint(13, 1.8),
                    ],
                    stroke_width=4,
                    color=ft.colors.with_opacity(0.5, ft.colors.LIGHT_GREEN),
                    stroke_cap_round=True,
                ),
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(1, 1),
                        ft.LineChartDataPoint(3, 2.8),
                        ft.LineChartDataPoint(7, 1.2),
                        ft.LineChartDataPoint(10, 2.8),
                        ft.LineChartDataPoint(12, 2.6),
                        ft.LineChartDataPoint(13, 3.9),
                    ],
                    color=ft.colors.with_opacity(0.5, ft.colors.PINK),
                    below_line_bgcolor=ft.colors.with_opacity(0.2, ft.colors.PINK),
                    stroke_width=4,
                    curved=True,
                    stroke_cap_round=True,
                ),
                ft.LineChartData(
                    data_points=[
                        ft.LineChartDataPoint(1, 3.8),
                        ft.LineChartDataPoint(3, 1.9),
                        ft.LineChartDataPoint(6, 5),
                        ft.LineChartDataPoint(10, 3.3),
                        ft.LineChartDataPoint(13, 4.5),
                    ],
                    color=ft.colors.with_opacity(0.5, ft.colors.CYAN),
                    stroke_width=4,
                    stroke_cap_round=True,
                ),
            ]

            chart = ft.LineChart(
                data_series=data_1,
                border=ft.Border(
                    bottom=ft.BorderSide(4, ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE))
                ),
                left_axis=ft.ChartAxis(
                    labels=[
                        ft.ChartAxisLabel(
                            value=1,
                            label=ft.Text("1m", size=14, weight=ft.FontWeight.BOLD),
                        ),
                        ft.ChartAxisLabel(
                            value=2,
                            label=ft.Text("2m", size=14, weight=ft.FontWeight.BOLD),
                        ),
                        ft.ChartAxisLabel(
                            value=3,
                            label=ft.Text("3m", size=14, weight=ft.FontWeight.BOLD),
                        ),
                        ft.ChartAxisLabel(
                            value=4,
                            label=ft.Text("4m", size=14, weight=ft.FontWeight.BOLD),
                        ),
                        ft.ChartAxisLabel(
                            value=5,
                            label=ft.Text("5m", size=14, weight=ft.FontWeight.BOLD),
                        ),
                        ft.ChartAxisLabel(
                            value=6,
                            label=ft.Text("6m", size=14, weight=ft.FontWeight.BOLD),
                        ),
                    ],
                    labels_size=40,
                ),
                bottom_axis=ft.ChartAxis(
                    labels=[
                        ft.ChartAxisLabel(
                            value=2,
                            label=ft.Container(
                                ft.Text(
                                    "SEP",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                                ),
                                margin=ft.margin.only(top=10),
                            ),
                        ),
                        ft.ChartAxisLabel(
                            value=7,
                            label=ft.Container(
                                ft.Text(
                                    "OCT",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                                ),
                                margin=ft.margin.only(top=10),
                            ),
                        ),
                        ft.ChartAxisLabel(
                            value=12,
                            label=ft.Container(
                                ft.Text(
                                    "DEC",
                                    size=16,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.with_opacity(0.5, ft.colors.ON_SURFACE),
                                ),
                                margin=ft.margin.only(top=10),
                            ),
                        ),
                    ],
                    labels_size=32,
                ),
                tooltip_bgcolor=ft.colors.with_opacity(0.8, ft.colors.BLUE_GREY),
                min_y=0,
                max_y=4,
                min_x=0,
                max_x=14,
                animate=100,
                expand=True,
            )

            def toggle_data(e):
                if s.toggle:
                    chart.data_series = data_2
                    chart.data_series[2].point = True
                    chart.max_y = 6
                    chart.interactive = False
                else:
                    chart.data_series = data_1
                    chart.max_y = 4
                    chart.interactive = True
                s.toggle = not s.toggle
                chart.update()

            page.add(ft.IconButton(ft.icons.REFRESH, on_click=toggle_data), ft.Container(content=chart, height=500))

        if nav_dest == 1:
            res = list(base.cur.execute(f"SELECT * FROM Reservation WHERE reservationUntil >= {int(time.time())}"))

            #nav_content = ft.Row([ft.Containerinf for inf ])
            print(res)
            nav_content = ft.Row([ft.Container(content=ft.Row([AnimatedCard(*inf)])) for inf in res])
            #nav_content = ft.Container(
                #content=ft.Row([AnimatedCard(*res[0])])
            #)
            page.add(nav_content)
            

        if nav_dest == 2:
            nav_content = get_base_template()
            page.add(nav_content)

        if nav_dest == 3:
            cal = FletCalendar(page)
            nav_content = ft.Container(
                content= ft.Column([cal, ft.ElevatedButton(text='Добавить запись', on_click=open_dlg)])
            )
            page.add(nav_content, cal.output)

    page.navigation_bar = ft.NavigationBar(
        destinations=[
            ft.NavigationDestination(
                icon=ft.icons.BAR_CHART_OUTLINED,
                selected_icon=ft.icons.BAR_CHART,
                label="График"
            ),
            ft.NavigationDestination(
                icon=ft.icons.SHOP_2_OUTLINED,
                selected_icon = ft.icons.SHOP_2,
                label="Витрина"
            ),
            ft.NavigationDestination(
                icon=ft.icons.DATA_OBJECT_OUTLINED,
                selected_icon=ft.icons.DATA_OBJECT,
                label="Редактировать базу"
            ),
            ft.NavigationDestination(
                icon=ft.icons.CALENDAR_VIEW_DAY_OUTLINED,
                selected_icon=ft.icons.CALENDAR_VIEW_DAY,
                label='Календарь',
            )
        ],
        on_change=change_content,
        selected_index=0
    )

    # a control's did_mount() is invoked right after it has been mounted
    page.navigation_bar.did_mount = lambda: synthetic_event(
        page=page, control=page.navigation_bar
    )

    # call the did_mount() once manually if you mess up the order of page.update()
    # page.navigation_bar.did_mount()
    page.update()


def synthetic_event(page: ft.Page, control: ft.NavigationBar):
    """
    Calls the control's event handler
    """
    control.on_change(
        ft.ControlEvent(
            target=control.uid,
            name="change",
            data=str(control.selected_index),
            control=control,
            page=page
        )
    )

ft.app(target=main)
base.con.close()
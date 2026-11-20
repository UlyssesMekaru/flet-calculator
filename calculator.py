import math
import re

import flet as ft

btn_head = [
    {'operador': 'AC', 'fonte': ft.Colors.BLACK, 'fundo': ft.Colors.GREY_100},
    {'operador': '+-', 'texto': '±', 'fonte': ft.Colors.BLACK, 'fundo': ft.Colors.GREY_100},
    {'operador': '%', 'fonte': ft.Colors.BLACK, 'fundo': ft.Colors.GREY_100},
    {'operador': '/', 'texto': '÷', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.ORANGE}
]

btn_middle = [
    {'operador': '7', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.WHITE_24},
    {'operador': '8', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.WHITE_24},
    {'operador': '9', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.WHITE_24},
    {'operador': '*', 'texto': '×', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.ORANGE},

    {'operador': '4', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.WHITE_24},
    {'operador': '5', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.WHITE_24},
    {'operador': '6', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.WHITE_24},
    {'operador': '-', 'texto': '−', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.ORANGE},

    {'operador': '1', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.WHITE_24},
    {'operador': '2', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.WHITE_24},
    {'operador': '3', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.WHITE_24},
    {'operador': '+', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.ORANGE},

    {'operador': '0', 'largura': 130, 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.WHITE_24},
    {'operador': '.', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.WHITE_24},
    {'operador': '=', 'fonte': ft.Colors.WHITE, 'fundo': ft.Colors.ORANGE}
]

keys = {
    'Enter': '=', 'Numpad Enter': '=', '=': '=',
    'Backspace': 'DEL', 'Escape': 'AC', 'Delete': 'AC',
    '+': '+', 'Numpad Add': '+',
    '-': '-', 'Numpad Subtract': '-',
    '*': '*', 'Numpad Multiply': '*',
    '/': '/', 'Numpad Divide': '/',
    '.': '.', ',': '.', 'Numpad Decimal': '.', 'Numpad Comma': '.',
    '%': '%'
}

shift_keys = {'8': '*', '=': '+', '5': '%'}


def format_value(value):
    if not math.isfinite(value):
        raise OverflowError
    if value == 0:
        value = 0
    return f'{value:.10g}'


def calculate(operador, value_at):
    value_at = value_at.rstrip('+-*/.')
    if not value_at or not set(value_at) <= set('0123456789.+-*/e'):
        raise ValueError
    value = eval(value_at, {'__builtins__': {}}, {})

    if operador == '%':
        value /= 100
    elif operador == '+-':
        value = -value

    return format_value(value)


def last_number(value_at):
    return re.search(r'[0-9.]*$', value_at).group()


def process(value_at, value, new_calc=False):
    if value_at == 'Erro':
        value_at, new_calc = '0', True

    if value == 'AC':
        return '0', False

    if value == 'DEL':
        if new_calc:
            return value_at, new_calc
        value_at = value_at[:-1]
        if value_at in ('', '-'):
            value_at = '0'
        return value_at, False

    if value.isdigit():
        if new_calc:
            value_at = '0'
        number = last_number(value_at)
        if len(number.replace('.', '')) >= 15:
            return value_at, False
        if number == '0':
            value_at = value_at[:-1]
        return value_at + value, False

    if value == '.':
        if new_calc:
            value_at = '0'
        number = last_number(value_at)
        if '.' in number:
            return value_at, False
        if not number:
            value_at += '0'
        return value_at + '.', False

    if value in ('/', '*', '-', '+'):
        if value_at[-1] in ('/', '.', '*', '+', '-'):
            value_at = value_at[:-1]
        return value_at + value, False

    if value in ('=', '%', '+-'):
        try:
            return calculate(operador=value, value_at=value_at), value == '='
        except (ArithmeticError, SyntaxError, ValueError):
            return 'Erro', True

    return value_at, new_calc


def read_key(key, shift=False):
    if shift and key in shift_keys:
        return shift_keys[key]
    if key.isdigit():
        return None if shift else key
    if key.startswith('Numpad ') and key[-1].isdigit():
        return key[-1]
    return keys.get(key)


def main(page: ft.Page):

    page.bgcolor = "#000"
    page.title = "Calculadora"
    page.padding = 15
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.window.width = 330
    page.window.height = 540
    page.window.resizable = False
    page.window.maximizable = False
    page.window.always_on_top = True

    value_at = '0'
    new_calc = False

    result = ft.Text(value="0", color=ft.Colors.WHITE, size=48, max_lines=1)

    def press(value):
        nonlocal value_at, new_calc
        value_at, new_calc = process(value_at, value, new_calc)

        text = value_at.replace('*', '×').replace('/', '÷').replace('-', '−')
        if len(text) > 20:
            text = '…' + text[-19:]

        if len(text) <= 7:
            result.size = 48
        elif len(text) <= 10:
            result.size = 36
        elif len(text) <= 14:
            result.size = 28
        else:
            result.size = 22

        result.value = text
        result.update()

    def select(e):
        press(e.control.data)

    def keyboard_event(e: ft.KeyboardEvent):
        value = read_key(e.key, e.shift)
        if value:
            press(value)

    def hover(e):
        e.control.opacity = 0.7 if e.data else 1
        e.control.update()

    display = ft.Container(
        content=result,
        width=270,
        height=90,
        alignment=ft.Alignment.BOTTOM_RIGHT,
        padding=ft.Padding.symmetric(horizontal=10)
    )

    btns = [ft.Container(
        content=ft.Text(value=btn.get('texto', btn['operador']), color=btn['fonte'], size=24),
        data=btn['operador'],
        width=btn.get('largura', 60),
        height=60,
        bgcolor=btn['fundo'],
        border_radius=100,
        alignment=ft.Alignment.CENTER,
        on_click=select,
        on_hover=hover
    ) for btn in btn_head + btn_middle]

    keyboard = ft.Row(
        width=270,
        wrap=True,
        spacing=10,
        run_spacing=10,
        controls=btns,
        alignment=ft.MainAxisAlignment.END
    )

    page.on_keyboard_event = keyboard_event
    page.add(display, keyboard)

ft.run(main)

# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 09:37:27 2022

@author: user
"""

#import shiny
#https://www.jayasekara.blog/2021/07/creating-interactive-dashboards-in-r-shiny-with-python-scripts.html

from shiny import App, render, ui

app_ui = ui.page_fluid(
    ui.input_slider("n", "N", 0, 100, 20),
    ui.output_text_verbatim("txt"),
)


def server(input, output, session):
    @output
    @render.text
    def txt():
        return f"n*2 is {input.n() * 2}"


app = App(app_ui, server)
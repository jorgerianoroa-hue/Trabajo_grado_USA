"""
Mercado laboral de Colombia (GEIH): análisis descriptivo.
Ejecutar con:  streamlit run app.py
"""

from pathlib import Path
from string import Template

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Mercado laboral de Colombia",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

DATA_PATH = Path(__file__).parent / "datos_reducidos.parquet"
MESES_ORDEN = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
               "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

# ---------------------------------------------------------------------------
# TOKENS DE DISEÑO
# Formal / promedio = PRIMARY · No formal = NOFORMAL (teal) · Mediana = ACCENT
# ---------------------------------------------------------------------------
BG, SURFACE = "#F8FAFC", "#FFFFFF"
TEXT, MUTED = "#111827", "#64748B"
PRIMARY, SECONDARY, ACCENT = "#164E63", "#0F766E", "#D97706"
NOFORMAL = "#5BA8A0"
BORDER, GRIDLINE = "#E2E8F0", "#EEF2F6"
F_DISPLAY, F_BODY = "Manrope", "Inter"

# Mapa de fondo de la portada: contorno simplificado de Colombia, matriz de puntos y retícula de coordenadas.
MAPA_SVG = '<svg class="cover-map" viewBox="0 0 1351 1814" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M169 0V1814M369 0V1814M569 0V1814M769 0V1814M969 0V1814M1169 0V1814M0 1714H1351M0 1514H1351M0 1314H1351M0 1114H1351M0 914H1351M0 714H1351M0 514H1351M0 314H1351M0 114H1351" fill="none" stroke="#164E63" stroke-opacity=".13" stroke-width="1" stroke-dasharray="2 8"/><text x="8" y="1707" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">4°S</text><text x="8" y="1507" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">2°S</text><text x="8" y="1307" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">0°</text><text x="8" y="1107" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">2°N</text><text x="8" y="907" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">4°N</text><text x="8" y="707" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">6°N</text><text x="8" y="507" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">8°N</text><text x="8" y="307" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">10°N</text><text x="8" y="107" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">12°N</text><text x="175" y="1806" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">78°O</text><text x="375" y="1806" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">76°O</text><text x="575" y="1806" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">74°O</text><text x="775" y="1806" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">72°O</text><text x="975" y="1806" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">70°O</text><text x="1175" y="1806" text-anchor="start" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">68°O</text><path d="M432 1329L389 1305L340 1272L311 1288L227 1274L202 1231L184 1233L84 1176L70 1145L107 1137L103 1087L126 1051L176 1044L218 981L256 929L219 905L238 847L216 755L237 729L221 645L181 591L194 543L226 550L245 520L222 461L234 447L285 450L360 380L402 369L403 336L421 252L478 205L541 204L549 183L628 191L706 141L745 118L794 70L829 76L855 102L836 136L772 153L746 203L708 232L679 269L666 340L639 399L690 405L703 451L725 473L733 513L721 550L725 571L749 580L773 615L902 605L960 618L1030 704L1071 693L1143 698L1200 687L1235 704L1217 758L1195 792L1187 863L1207 930L1235 959L1239 982L1188 1032L1224 1054L1251 1089L1281 1188L1263 1201L1243 1142L1215 1110L1182 1144L987 1142L989 1205L1047 1215L1044 1253L1024 1243L968 1260L967 1332L1011 1369L1027 1426L1025 1469L980 1744L930 1690L900 1688L964 1586L888 1539L828 1548L792 1531L737 1557L662 1545L603 1440L557 1414L525 1367L458 1319L432 1329Z" fill="#164E63" fill-opacity=".04" stroke="#164E63" stroke-opacity=".4" stroke-width="2" stroke-linejoin="round"/><path d="M970 1692h0M925 1666h0M955 1666h0M985 1666h0M940 1640h0M970 1640h0M985 1614h0M955 1562h0M985 1562h0M670 1536h0M700 1536h0M730 1536h0M760 1536h0M820 1536h0M850 1536h0M910 1536h0M940 1536h0M970 1536h0M1000 1536h0M655 1510h0M685 1510h0M715 1510h0M745 1510h0M775 1510h0M805 1510h0M835 1510h0M865 1510h0M895 1510h0M925 1510h0M955 1510h0M985 1510h0M640 1484h0M670 1484h0M700 1484h0M730 1484h0M760 1484h0M790 1484h0M820 1484h0M850 1484h0M880 1484h0M910 1484h0M940 1484h0M970 1484h0M1000 1484h0M625 1458h0M655 1458h0M685 1458h0M715 1458h0M745 1458h0M775 1458h0M805 1458h0M835 1458h0M865 1458h0M895 1458h0M925 1458h0M955 1458h0M985 1458h0M1015 1458h0M610 1432h0M640 1432h0M670 1432h0M700 1432h0M730 1432h0M760 1432h0M790 1432h0M820 1432h0M850 1432h0M880 1432h0M910 1432h0M940 1432h0M970 1432h0M1000 1432h0M565 1406h0M595 1406h0M625 1406h0M655 1406h0M685 1406h0M715 1406h0M745 1406h0M775 1406h0M805 1406h0M835 1406h0M865 1406h0M895 1406h0M925 1406h0M955 1406h0M985 1406h0M550 1380h0M580 1380h0M610 1380h0M640 1380h0M670 1380h0M700 1380h0M730 1380h0M760 1380h0M790 1380h0M820 1380h0M850 1380h0M880 1380h0M910 1380h0M940 1380h0M970 1380h0M1000 1380h0M535 1354h0M565 1354h0M595 1354h0M625 1354h0M655 1354h0M685 1354h0M715 1354h0M745 1354h0M775 1354h0M805 1354h0M835 1354h0M865 1354h0M895 1354h0M925 1354h0M955 1354h0M490 1328h0M520 1328h0M550 1328h0M580 1328h0M610 1328h0M640 1328h0M670 1328h0M700 1328h0M730 1328h0M760 1328h0M790 1328h0M820 1328h0M850 1328h0M880 1328h0M910 1328h0M940 1328h0M415 1302h0M445 1302h0M475 1302h0M505 1302h0M535 1302h0M565 1302h0M595 1302h0M625 1302h0M655 1302h0M685 1302h0M715 1302h0M745 1302h0M775 1302h0M805 1302h0M835 1302h0M865 1302h0M895 1302h0M925 1302h0M955 1302h0M310 1276h0M370 1276h0M400 1276h0M430 1276h0M460 1276h0M490 1276h0M520 1276h0M550 1276h0M580 1276h0M610 1276h0M640 1276h0M670 1276h0M700 1276h0M730 1276h0M760 1276h0M790 1276h0M820 1276h0M850 1276h0M880 1276h0M910 1276h0M940 1276h0M235 1250h0M265 1250h0M295 1250h0M325 1250h0M355 1250h0M385 1250h0M415 1250h0M445 1250h0M475 1250h0M505 1250h0M535 1250h0M565 1250h0M595 1250h0M625 1250h0M655 1250h0M685 1250h0M715 1250h0M745 1250h0M775 1250h0M805 1250h0M835 1250h0M865 1250h0M895 1250h0M925 1250h0M955 1250h0M190 1224h0M220 1224h0M250 1224h0M280 1224h0M310 1224h0M340 1224h0M370 1224h0M400 1224h0M430 1224h0M460 1224h0M490 1224h0M520 1224h0M550 1224h0M580 1224h0M610 1224h0M640 1224h0M670 1224h0M700 1224h0M730 1224h0M760 1224h0M790 1224h0M820 1224h0M850 1224h0M880 1224h0M910 1224h0M940 1224h0M970 1224h0M1000 1224h0M1030 1224h0M145 1198h0M175 1198h0M205 1198h0M235 1198h0M265 1198h0M295 1198h0M325 1198h0M355 1198h0M385 1198h0M415 1198h0M445 1198h0M475 1198h0M505 1198h0M535 1198h0M565 1198h0M595 1198h0M625 1198h0M655 1198h0M685 1198h0M715 1198h0M745 1198h0M775 1198h0M805 1198h0M835 1198h0M865 1198h0M895 1198h0M925 1198h0M955 1198h0M100 1172h0M130 1172h0M160 1172h0M190 1172h0M220 1172h0M250 1172h0M280 1172h0M310 1172h0M340 1172h0M370 1172h0M400 1172h0M430 1172h0M460 1172h0M490 1172h0M520 1172h0M550 1172h0M580 1172h0M610 1172h0M640 1172h0M670 1172h0M700 1172h0M730 1172h0M760 1172h0M790 1172h0M820 1172h0M850 1172h0M880 1172h0M910 1172h0M940 1172h0M970 1172h0M115 1146h0M145 1146h0M175 1146h0M205 1146h0M235 1146h0M265 1146h0M295 1146h0M325 1146h0M355 1146h0M385 1146h0M415 1146h0M445 1146h0M475 1146h0M505 1146h0M535 1146h0M565 1146h0M595 1146h0M625 1146h0M655 1146h0M685 1146h0M715 1146h0M745 1146h0M775 1146h0M805 1146h0M835 1146h0M865 1146h0M895 1146h0M925 1146h0M955 1146h0M1255 1146h0M130 1120h0M160 1120h0M190 1120h0M220 1120h0M250 1120h0M280 1120h0M310 1120h0M340 1120h0M370 1120h0M400 1120h0M430 1120h0M460 1120h0M490 1120h0M520 1120h0M550 1120h0M580 1120h0M610 1120h0M640 1120h0M670 1120h0M700 1120h0M730 1120h0M760 1120h0M790 1120h0M820 1120h0M850 1120h0M880 1120h0M910 1120h0M940 1120h0M970 1120h0M1000 1120h0M1030 1120h0M1060 1120h0M1090 1120h0M1120 1120h0M1150 1120h0M1180 1120h0M1240 1120h0M115 1094h0M145 1094h0M175 1094h0M205 1094h0M235 1094h0M265 1094h0M295 1094h0M325 1094h0M355 1094h0M385 1094h0M415 1094h0M445 1094h0M475 1094h0M505 1094h0M535 1094h0M565 1094h0M595 1094h0M625 1094h0M655 1094h0M685 1094h0M715 1094h0M745 1094h0M775 1094h0M805 1094h0M835 1094h0M865 1094h0M895 1094h0M925 1094h0M955 1094h0M985 1094h0M1015 1094h0M1045 1094h0M1075 1094h0M1105 1094h0M1135 1094h0M1165 1094h0M1195 1094h0M1225 1094h0M130 1068h0M160 1068h0M190 1068h0M220 1068h0M250 1068h0M280 1068h0M310 1068h0M340 1068h0M370 1068h0M400 1068h0M430 1068h0M460 1068h0M490 1068h0M520 1068h0M550 1068h0M580 1068h0M610 1068h0M640 1068h0M670 1068h0M700 1068h0M730 1068h0M760 1068h0M790 1068h0M820 1068h0M850 1068h0M880 1068h0M910 1068h0M940 1068h0M970 1068h0M1000 1068h0M1030 1068h0M1060 1068h0M1090 1068h0M1120 1068h0M1150 1068h0M1180 1068h0M1210 1068h0M205 1042h0M235 1042h0M265 1042h0M295 1042h0M325 1042h0M355 1042h0M385 1042h0M415 1042h0M445 1042h0M475 1042h0M505 1042h0M535 1042h0M565 1042h0M595 1042h0M625 1042h0M655 1042h0M685 1042h0M715 1042h0M745 1042h0M775 1042h0M805 1042h0M835 1042h0M865 1042h0M895 1042h0M925 1042h0M955 1042h0M985 1042h0M1015 1042h0M1045 1042h0M1075 1042h0M1105 1042h0M1135 1042h0M1165 1042h0M220 1016h0M250 1016h0M280 1016h0M310 1016h0M340 1016h0M370 1016h0M400 1016h0M430 1016h0M460 1016h0M490 1016h0M520 1016h0M550 1016h0M580 1016h0M610 1016h0M640 1016h0M670 1016h0M700 1016h0M730 1016h0M760 1016h0M790 1016h0M820 1016h0M850 1016h0M880 1016h0M910 1016h0M940 1016h0M970 1016h0M1000 1016h0M1030 1016h0M1060 1016h0M1090 1016h0M1120 1016h0M1150 1016h0M1180 1016h0M235 990h0M265 990h0M295 990h0M325 990h0M355 990h0M385 990h0M415 990h0M445 990h0M475 990h0M505 990h0M535 990h0M565 990h0M595 990h0M625 990h0M655 990h0M685 990h0M715 990h0M745 990h0M775 990h0M805 990h0M835 990h0M865 990h0M895 990h0M925 990h0M955 990h0M985 990h0M1015 990h0M1045 990h0M1075 990h0M1105 990h0M1135 990h0M1165 990h0M1195 990h0M250 964h0M280 964h0M310 964h0M340 964h0M370 964h0M400 964h0M430 964h0M460 964h0M490 964h0M520 964h0M550 964h0M580 964h0M610 964h0M640 964h0M670 964h0M700 964h0M730 964h0M760 964h0M790 964h0M820 964h0M850 964h0M880 964h0M910 964h0M940 964h0M970 964h0M1000 964h0M1030 964h0M1060 964h0M1090 964h0M1120 964h0M1150 964h0M1180 964h0M1210 964h0M265 938h0M295 938h0M325 938h0M355 938h0M385 938h0M415 938h0M445 938h0M475 938h0M505 938h0M535 938h0M565 938h0M595 938h0M625 938h0M655 938h0M685 938h0M715 938h0M745 938h0M775 938h0M805 938h0M835 938h0M865 938h0M895 938h0M925 938h0M955 938h0M985 938h0M1015 938h0M1045 938h0M1075 938h0M1105 938h0M1135 938h0M1165 938h0M1195 938h0M250 912h0M280 912h0M310 912h0M340 912h0M370 912h0M400 912h0M430 912h0M460 912h0M490 912h0M520 912h0M550 912h0M580 912h0M610 912h0M640 912h0M670 912h0M700 912h0M730 912h0M760 912h0M790 912h0M820 912h0M850 912h0M880 912h0M910 912h0M940 912h0M970 912h0M1000 912h0M1030 912h0M1060 912h0M1090 912h0M1120 912h0M1150 912h0M1180 912h0M235 886h0M265 886h0M295 886h0M325 886h0M355 886h0M385 886h0M415 886h0M445 886h0M475 886h0M505 886h0M535 886h0M565 886h0M595 886h0M625 886h0M655 886h0M685 886h0M715 886h0M745 886h0M775 886h0M805 886h0M835 886h0M865 886h0M895 886h0M925 886h0M955 886h0M985 886h0M1015 886h0M1045 886h0M1075 886h0M1105 886h0M1135 886h0M1165 886h0M250 860h0M280 860h0M310 860h0M340 860h0M370 860h0M400 860h0M430 860h0M460 860h0M490 860h0M520 860h0M550 860h0M580 860h0M610 860h0M640 860h0M670 860h0M700 860h0M730 860h0M760 860h0M790 860h0M820 860h0M850 860h0M880 860h0M910 860h0M940 860h0M970 860h0M1000 860h0M1030 860h0M1060 860h0M1090 860h0M1120 860h0M1150 860h0M1180 860h0M265 834h0M295 834h0M325 834h0M355 834h0M385 834h0M415 834h0M445 834h0M475 834h0M505 834h0M535 834h0M565 834h0M595 834h0M625 834h0M655 834h0M685 834h0M715 834h0M745 834h0M775 834h0M805 834h0M835 834h0M865 834h0M895 834h0M925 834h0M955 834h0M985 834h0M1015 834h0M1045 834h0M1075 834h0M1105 834h0M1135 834h0M1165 834h0M250 808h0M280 808h0M310 808h0M340 808h0M370 808h0M400 808h0M430 808h0M460 808h0M490 808h0M520 808h0M550 808h0M580 808h0M610 808h0M640 808h0M670 808h0M700 808h0M730 808h0M760 808h0M790 808h0M820 808h0M850 808h0M880 808h0M910 808h0M940 808h0M970 808h0M1000 808h0M1030 808h0M1060 808h0M1090 808h0M1120 808h0M1150 808h0M1180 808h0M235 782h0M265 782h0M295 782h0M325 782h0M355 782h0M385 782h0M415 782h0M445 782h0M475 782h0M505 782h0M535 782h0M565 782h0M595 782h0M625 782h0M655 782h0M685 782h0M715 782h0M745 782h0M775 782h0M805 782h0M835 782h0M865 782h0M895 782h0M925 782h0M955 782h0M985 782h0M1015 782h0M1045 782h0M1075 782h0M1105 782h0M1135 782h0M1165 782h0M250 756h0M280 756h0M310 756h0M340 756h0M370 756h0M400 756h0M430 756h0M460 756h0M490 756h0M520 756h0M550 756h0M580 756h0M610 756h0M640 756h0M670 756h0M700 756h0M730 756h0M760 756h0M790 756h0M820 756h0M850 756h0M880 756h0M910 756h0M940 756h0M970 756h0M1000 756h0M1030 756h0M1060 756h0M1090 756h0M1120 756h0M1150 756h0M1180 756h0M265 730h0M295 730h0M325 730h0M355 730h0M385 730h0M415 730h0M445 730h0M475 730h0M505 730h0M535 730h0M565 730h0M595 730h0M625 730h0M655 730h0M685 730h0M715 730h0M745 730h0M775 730h0M805 730h0M835 730h0M865 730h0M895 730h0M925 730h0M955 730h0M985 730h0M1015 730h0M1045 730h0M1075 730h0M1105 730h0M1135 730h0M1165 730h0M1195 730h0M250 704h0M280 704h0M310 704h0M340 704h0M370 704h0M400 704h0M430 704h0M460 704h0M490 704h0M520 704h0M550 704h0M580 704h0M610 704h0M640 704h0M670 704h0M700 704h0M730 704h0M760 704h0M790 704h0M820 704h0M850 704h0M880 704h0M910 704h0M940 704h0M970 704h0M1000 704h0M1060 704h0M1090 704h0M1120 704h0M1150 704h0M1180 704h0M1210 704h0M235 678h0M265 678h0M295 678h0M325 678h0M355 678h0M385 678h0M415 678h0M445 678h0M475 678h0M505 678h0M535 678h0M565 678h0M595 678h0M625 678h0M655 678h0M685 678h0M715 678h0M745 678h0M775 678h0M805 678h0M835 678h0M865 678h0M895 678h0M925 678h0M955 678h0M985 678h0M250 652h0M280 652h0M310 652h0M340 652h0M370 652h0M400 652h0M430 652h0M460 652h0M490 652h0M520 652h0M550 652h0M580 652h0M610 652h0M640 652h0M670 652h0M700 652h0M730 652h0M760 652h0M790 652h0M820 652h0M850 652h0M880 652h0M910 652h0M940 652h0M970 652h0M235 626h0M265 626h0M295 626h0M325 626h0M355 626h0M385 626h0M415 626h0M445 626h0M475 626h0M505 626h0M535 626h0M565 626h0M595 626h0M625 626h0M655 626h0M685 626h0M715 626h0M745 626h0M775 626h0M805 626h0M835 626h0M865 626h0M895 626h0M925 626h0M955 626h0M220 600h0M250 600h0M280 600h0M310 600h0M340 600h0M370 600h0M400 600h0M430 600h0M460 600h0M490 600h0M520 600h0M550 600h0M580 600h0M610 600h0M640 600h0M670 600h0M700 600h0M730 600h0M205 574h0M235 574h0M265 574h0M295 574h0M325 574h0M355 574h0M385 574h0M415 574h0M445 574h0M475 574h0M505 574h0M535 574h0M565 574h0M595 574h0M625 574h0M655 574h0M685 574h0M715 574h0M250 548h0M280 548h0M310 548h0M340 548h0M370 548h0M400 548h0M430 548h0M460 548h0M490 548h0M520 548h0M550 548h0M580 548h0M610 548h0M640 548h0M670 548h0M700 548h0M265 522h0M295 522h0M325 522h0M355 522h0M385 522h0M415 522h0M445 522h0M475 522h0M505 522h0M535 522h0M565 522h0M595 522h0M625 522h0M655 522h0M685 522h0M715 522h0M250 497h0M280 497h0M310 497h0M340 497h0M370 497h0M400 497h0M430 497h0M460 497h0M490 497h0M520 497h0M550 497h0M580 497h0M610 497h0M640 497h0M670 497h0M700 497h0M235 471h0M265 471h0M295 471h0M325 471h0M355 471h0M385 471h0M415 471h0M445 471h0M475 471h0M505 471h0M535 471h0M565 471h0M595 471h0M625 471h0M655 471h0M685 471h0M310 445h0M340 445h0M370 445h0M400 445h0M430 445h0M460 445h0M490 445h0M520 445h0M550 445h0M580 445h0M610 445h0M640 445h0M670 445h0M355 419h0M385 419h0M415 419h0M445 419h0M475 419h0M505 419h0M535 419h0M565 419h0M595 419h0M625 419h0M655 419h0M685 419h0M370 393h0M400 393h0M430 393h0M460 393h0M490 393h0M520 393h0M550 393h0M580 393h0M610 393h0M415 367h0M445 367h0M475 367h0M505 367h0M535 367h0M565 367h0M595 367h0M625 367h0M430 341h0M460 341h0M490 341h0M520 341h0M550 341h0M580 341h0M610 341h0M640 341h0M415 315h0M445 315h0M475 315h0M505 315h0M535 315h0M565 315h0M595 315h0M625 315h0M655 315h0M430 289h0M460 289h0M490 289h0M520 289h0M550 289h0M580 289h0M610 289h0M640 289h0M445 263h0M475 263h0M505 263h0M535 263h0M565 263h0M595 263h0M625 263h0M655 263h0M460 237h0M490 237h0M520 237h0M550 237h0M580 237h0M610 237h0M640 237h0M670 237h0M535 211h0M565 211h0M595 211h0M625 211h0M655 211h0M685 211h0M715 211h0M670 185h0M700 185h0M730 185h0M715 159h0M745 159h0M760 133h0M790 133h0M820 133h0M775 107h0M805 107h0M835 107h0" fill="none" stroke="#164E63" stroke-opacity=".24" stroke-width="11" stroke-linecap="round"/></svg>'

CSS = Template("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@500;600;700&display=swap');
html, body, [class*="css"], .stApp { font-family:'$F_BODY',sans-serif; color:$TEXT; }
.stApp { background:$BG; }
.block-container { max-width:1440px; padding:1.2rem 2.4rem 3rem; }
header[data-testid="stHeader"] { background:transparent; }
footer { visibility:hidden; }
h1,h2,h3 { font-family:'$F_DISPLAY',sans-serif; }

/* Navegación superior */
.brand { font-family:'$F_DISPLAY',sans-serif; font-weight:700; font-size:1.1rem; color:$PRIMARY; letter-spacing:-0.01em; padding-top:.3rem; }
.st-key-nav button { width:auto; min-height:0; padding:.35rem 0 .45rem; background:transparent; border:none;
    border-bottom:2px solid transparent; border-radius:0; color:$MUTED; font-weight:500; font-size:.95rem;
    transition:color .15s, border-color .15s; }
.st-key-nav button:hover { color:$TEXT; background:transparent; border-bottom-color:$BORDER; }
.st-key-nav button[kind="primary"], .st-key-nav button[data-testid="stBaseButton-primary"],
.st-key-nav button[kind="primary"]:hover, .st-key-nav button[data-testid="stBaseButton-primary"]:hover {
    color:$PRIMARY; font-weight:600; border-bottom-color:$PRIMARY; background:transparent; }
.st-key-nav button p, div[class*="st-key-link_"] button p { color:inherit; font-size:inherit; font-weight:inherit; }

/* Enlaces de texto (Explorar →) */
div[class*="st-key-link_"] button { width:auto; min-height:0; padding:0; background:transparent; border:none;
    color:$PRIMARY; font-weight:500; font-size:.95rem; justify-content:flex-start; transition:color .15s; }
div[class*="st-key-link_"] button:hover { color:$SECONDARY; background:transparent; text-decoration:underline; text-underline-offset:4px; }

/* Filtros compactos */
.st-key-filters label p { font-size:.78rem; color:$MUTED; font-weight:500; }
.st-key-filters [data-baseweb="select"] > div { background:$SURFACE; border:1px solid $BORDER; border-radius:8px; min-height:38px; font-size:.88rem; }
.st-key-filters [data-baseweb="tag"] { background:#E4EEF1; color:$PRIMARY; border-radius:6px; }
.aux { color:$MUTED; font-size:.84rem; margin:.3rem 0 1rem; }

/* Tipografía editorial */
.page-title { font-family:'$F_DISPLAY',sans-serif; font-size:2.2rem; font-weight:600; letter-spacing:-0.02em; margin-top:1.4rem; }
.page-sub { color:$MUTED; font-size:1.02rem; margin-top:.3rem; max-width:480px; }
.tag { color:$ACCENT; font-size:.78rem; font-weight:500; border:1px solid $ACCENT; border-radius:999px; padding:0 .5rem; margin-left:.6rem; }
.chart-title { font-family:'$F_DISPLAY',sans-serif; font-size:1rem; font-weight:600; margin:1.6rem 0 .2rem; }
.rule { border:none; border-top:1px solid $BORDER; margin:1rem 0 1.2rem; }
.foot { border-top:1px solid $BORDER; color:$MUTED; font-size:.82rem; margin-top:4rem; padding-top:1rem; }
.canvas-empty { min-height:460px; border:1px dashed $BORDER; border-radius:10px; display:flex; align-items:center; justify-content:center; color:$MUTED; font-size:.95rem; margin-top:1.5rem; }

/* KPIs: número grande + etiqueta + divisor vertical */
.kpi-v { font-family:'$F_BODY',sans-serif; font-size:2.4rem; font-weight:600; line-height:1.1; letter-spacing:-0.02em; font-variant-numeric:tabular-nums; }
.kpi-l { color:$MUTED; font-size:.88rem; margin-top:.2rem; }
.k-primary { color:$PRIMARY; } .k-teal { color:$SECONDARY; } .k-accent { color:$ACCENT; }
.st-key-kpis [data-testid="stColumn"]:not(:first-child), .st-key-kpis [data-testid="column"]:not(:first-child) {
    border-left:1px solid $BORDER; padding-left:1.5rem; }

/* Tabs minimalistas */
.stTabs [data-baseweb="tab-list"] { gap:1.7rem; border-bottom:1px solid $BORDER; background:transparent; }
.stTabs [data-baseweb="tab"] { background:transparent; padding:.5rem 0; color:$MUTED; font-weight:500; font-size:.95rem; transition:color .15s; }
.stTabs [data-baseweb="tab"]:hover { color:$TEXT; background:transparent; }
.stTabs [aria-selected="true"] { color:$TEXT; font-weight:600; }
.stTabs [data-baseweb="tab-highlight"] { background:$PRIMARY; height:2px; }
.stTabs [data-baseweb="tab-border"] { background:transparent; }

/* Asistente virtual: panel de chat fijo a la derecha, visible en todas las secciones */
[data-testid="stToolbar"] { display:none; }
.st-key-chat { position:fixed; top:0; right:0; bottom:0; width:380px !important; z-index:100; background:$SURFACE;
    border-left:1px solid $BORDER; padding:1.4rem 1.2rem 1rem; overflow-y:auto; }
.chat-title { font-family:'$F_DISPLAY',sans-serif; font-size:1.2rem; font-weight:600; }
.chat-sub { color:$MUTED; font-size:.9rem; margin-top:.2rem; }
.st-key-chat [data-testid="stChatMessage"] { background:transparent; padding:.35rem 0; }
.st-key-chat [data-testid="stChatInput"] { border:1px solid $BORDER; border-radius:10px; background:$SURFACE; }
div[class*="st-key-sug_"] button { width:100%; min-height:0; justify-content:flex-start; text-align:left; background:transparent;
    border:none; border-top:1px solid $BORDER; border-radius:0; padding:.55rem 0; color:$TEXT; font-size:.9rem; font-weight:400; transition:color .15s; }
div[class*="st-key-sug_"] button:hover { color:$PRIMARY; background:transparent; }
div[class*="st-key-sug_"] button p { color:inherit; font-size:inherit; }
.st-key-chat_reset button { width:auto; min-height:0; padding:0; background:transparent; border:none; color:$MUTED; font-size:.84rem; }
.st-key-chat_reset button:hover { color:$PRIMARY; background:transparent; text-decoration:underline; }
@media (min-width:1100px) { .block-container { max-width:none; padding-right:420px; } }
@media (max-width:1099px) { .st-key-chat { position:static; width:100% !important; border-left:none;
    border-top:1px solid $BORDER; margin-top:2rem; padding:1.2rem 0 0; } }

/* Portada */
.cover-map { position:fixed; top:0; left:0; width:100vw; height:100vh; z-index:0; pointer-events:none; padding:2vh 0; box-sizing:border-box; }
.cover-content { position:relative; z-index:1; text-align:center; padding-top:17vh; }
.cover-eyebrow { color:$SECONDARY; font-weight:500; font-size:.95rem; margin-bottom:1rem; }
.cover-title { font-family:'$F_DISPLAY',sans-serif; font-size:4.6rem; font-weight:600; line-height:1.04; letter-spacing:-0.03em; }
.cover-sub { color:$MUTED; font-size:1.2rem; line-height:1.5; margin:1.2rem auto 0; max-width:520px; }
.cover-foot { position:fixed; bottom:1.2rem; left:0; right:0; text-align:center; color:$MUTED; font-size:.82rem; z-index:1; }
.st-key-cover_cta { position:relative; z-index:1; margin-top:2rem; }
.st-key-cover_cta button { width:100%; background:$PRIMARY; color:#FFFFFF; border:none; border-radius:8px;
    padding:.75rem 2rem; font-size:1rem; font-weight:500; transition:background .15s; }
.st-key-cover_cta button:hover { background:$SECONDARY; color:#FFFFFF; }
.st-key-cover_cta button p { color:inherit; font-size:inherit; }
@media (min-width:1100px) { .block-container:has(.cover-content) { padding-right:2.4rem; } }
@media (max-width:900px) { .cover-title { font-size:2.8rem; } .cover-content { padding-top:12vh; } }

@media (max-width:900px) {
    .block-container { padding:1rem 1rem 2rem; }
    .st-key-nav [data-testid="stHorizontalBlock"] { flex-wrap:wrap; gap:.2rem 1.3rem; }
    .st-key-nav [data-testid="stColumn"] { min-width:0 !important; flex:0 0 auto !important; width:auto !important; }
    .st-key-nav [data-testid="stColumn"]:first-child { flex:1 0 100% !important; }
    .st-key-kpis [data-testid="stColumn"]:not(:first-child) { border-left:none; padding-left:0; }
}
</style>
""")


def inject_css():
    st.markdown(CSS.safe_substitute(
        F_BODY=F_BODY, F_DISPLAY=F_DISPLAY, TEXT=TEXT, BG=BG, SURFACE=SURFACE, MUTED=MUTED,
        PRIMARY=PRIMARY, SECONDARY=SECONDARY, ACCENT=ACCENT, BORDER=BORDER,
    ), unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# FORMATO (separadores colombianos: 1.850.000 y 61,4%)
# ---------------------------------------------------------------------------
def fmt_n(x):
    return f"{x:,.0f}".replace(",", ".")


def fmt_cop(x):
    return "$" + fmt_n(x)


def fmt_pct(x):
    return f"{x:.1%}".replace(".", ",")


# ---------------------------------------------------------------------------
# CARGA DE DATOS Y MEDIDAS (sin cambios de lógica)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner="Cargando datos...")
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_parquet(path)
    df["Mes Letras"] = pd.Categorical(
        df["mes"].map(dict(zip(range(1, 13), MESES_ORDEN))),
        categories=MESES_ORDEN, ordered=True,
    )
    for c in ["departamento", "sexo", "estado_civil", "etnia", "nivel_educativo",
              "tipo_contrato", "posicion_ocupacional", "lugar_trabajo",
              "sector_economico_seccion", "oficio_gran_grupo"]:
        df[c] = df[c].astype("category")
    return df


def pct_formal_no_formal(df):
    if len(df) == 0:
        return 0.0, 0.0
    return (df["empleo_formal_pleno"] == 1).sum() / len(df), (df["empleo_formal_pleno"] == 0).sum() / len(df)


def promedio_mediana_ingreso(df):
    if len(df) == 0:
        return 0.0, 0.0
    return df["ingreso_laboral_total"].mean(), df["ingreso_laboral_total"].median()


def agrupar(df, dim, col, funcs, por_n=True):
    out = df.groupby(dim, observed=True)[col].agg([*funcs, "count"]).reset_index()
    out.columns = [dim, *funcs, "n"]
    return out.sort_values("n", ascending=False) if por_n else out.sort_values(dim)


# ---------------------------------------------------------------------------
# TEMA PLOTLY CENTRALIZADO
# ---------------------------------------------------------------------------
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family=F_BODY, size=12, color=MUTED),
    legend=dict(orientation="h", yanchor="bottom", y=1.0, x=0, title=dict(text=""),
                font=dict(size=12, color=MUTED)),
    margin=dict(t=34, b=8, l=4, r=16),
    hoverlabel=dict(bgcolor=SURFACE, bordercolor=BORDER, font=dict(family=F_BODY, size=12, color=TEXT)),
    separators=",.",
    bargap=0.4,
)
PLOT_CONFIG = {"displayModeBar": False}


def estilizar_figura(fig, altura, pct, horizontal, apilado=False, margen_der=16):
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(height=altura, barmode="stack" if apilado else "group",
                      margin=dict(t=34, b=8, l=4, r=margen_der))
    valor = dict(showgrid=True, gridcolor=GRIDLINE, zeroline=False, showline=False,
                 tickfont=dict(size=11), tickformat=".0%" if pct else ",.0f",
                 tickprefix="" if pct else "$")
    if pct and horizontal:
        valor["range"] = [0, 1]
    categoria = dict(showgrid=False, zeroline=False, showline=False, ticks="", type="category",
                     automargin=True, tickfont=dict(size=12, color=TEXT))
    if horizontal:
        fig.update_xaxes(**valor)
        fig.update_yaxes(**categoria)
    else:
        fig.update_yaxes(**valor)
        fig.update_xaxes(**categoria)
    return fig


def grafico_barras(d, dim, series, pct, apilado=False, marcador=None, key=None):
    """Barras horizontales (ranking). series: (nombre, columna, color, color_texto)."""
    cat = d[dim].astype(str)
    fmt, pre = ".1%" if pct else ",.0f", "" if pct else "$"
    fig = go.Figure()
    for nombre, col, color, txt in series:
        fig.add_bar(
            name=nombre, y=cat, x=d[col], orientation="h", marker=dict(color=color),
            customdata=d["n"], texttemplate=f"{pre}%{{x:{fmt}}}", cliponaxis=False,
            textposition="inside" if apilado else "outside", textfont=dict(color=txt, size=11),
            hovertemplate=f"<b>%{{y}}</b><br>{nombre}: {pre}%{{x:{fmt}}}<br>Registros: %{{customdata:,}}<extra></extra>",
        )
    if marcador:
        nombre, col, color = marcador
        fig.add_scatter(
            name=nombre, y=cat, x=d[col], mode="markers", customdata=d["n"],
            marker=dict(symbol="diamond", size=9, color=color, line=dict(color=SURFACE, width=1)),
            hovertemplate=f"<b>%{{y}}</b><br>{nombre}: {pre}%{{x:{fmt}}}<extra></extra>",
        )
    estilizar_figura(fig, max(240, 30 * len(d) + 90), pct, True, apilado, margen_der=16 if pct else 70)
    st.plotly_chart(fig, config=PLOT_CONFIG, key=key)


def grafico_tendencia(d, dim, series, pct, key=None):
    """Líneas finas con punto pequeño; etiqueta solo en el último punto. series: (nombre, columna, color)."""
    x = d[dim].astype(str)
    fmt, pre = ".1%" if pct else ",.0f", "" if pct else "$"
    fig = go.Figure()
    for nombre, col, color in series:
        y = d[col]
        etiquetas = [""] * (len(d) - 1) + [fmt_pct(y.iloc[-1]) if pct else fmt_cop(y.iloc[-1])]
        fig.add_scatter(
            name=nombre, x=x, y=y, mode="lines+markers+text", text=etiquetas,
            textposition="top center", textfont=dict(color=color, size=11), cliponaxis=False,
            line=dict(color=color, width=2), marker=dict(size=6, color=color),
            hovertemplate=f"<b>%{{x}}</b><br>{nombre}: {pre}%{{y:{fmt}}}<extra></extra>",
        )
    estilizar_figura(fig, 320, pct, False, margen_der=40)
    st.plotly_chart(fig, config=PLOT_CONFIG, key=key)


def titulo_grafico(texto):
    st.markdown(f'<div class="chart-title">{texto}</div>', unsafe_allow_html=True)


def sin_datos():
    st.caption("No hay registros para los filtros seleccionados.")


def grafico_formalidad(df, dim, titulo, tendencia=False):
    titulo_grafico(titulo)
    if df.empty:
        return sin_datos()
    d = agrupar(df, dim, "empleo_formal_pleno", ["mean"], por_n=not tendencia)
    d["no"] = 1 - d["mean"]
    series = [("Trabajo formal", "mean", PRIMARY, "#FFFFFF"), ("Trabajo no formal", "no", NOFORMAL, TEXT)]
    if tendencia:
        grafico_tendencia(d, dim, [s[:3] for s in series], True, key=f"ch_formalidad_{dim}")
    else:
        grafico_barras(d.sort_values("mean"), dim, series, True, apilado=True, key=f"ch_formalidad_{dim}")


def grafico_ingreso(df, dim, titulo, tendencia=False):
    titulo_grafico(titulo)
    if df.empty:
        return sin_datos()
    d = agrupar(df, dim, "ingreso_laboral_total", ["mean", "median"], por_n=not tendencia)
    if tendencia:
        grafico_tendencia(d, dim, [("Promedio", "mean", PRIMARY), ("Mediana", "median", ACCENT)],
                          False, key=f"ch_ingreso_{dim}")
    else:
        grafico_barras(d.sort_values("mean"), dim, [("Promedio", "mean", PRIMARY, MUTED)], False,
                       marcador=("Mediana", "median", ACCENT), key=f"ch_ingreso_{dim}")


# Organización por pestañas: cada fila es una lista de gráficos que se muestran lado a lado
GRUPOS = [
    ("Departamento", [[("departamento", "Por departamento", {})]]),
    ("Tiempo", [[("anio", "Por año", {"tendencia": True}), ("Mes Letras", "Por mes", {"tendencia": True})]]),
    ("Educación", [[("nivel_educativo", "Por nivel educativo", {})]]),
    ("Demografía", [[("sexo", "Por sexo", {}), ("estado_civil", "Por estado civil", {})],
                    [("etnia", "Por etnia", {})]]),
    ("Contrato", [[("tipo_contrato", "Por tipo de contrato", {}), ("posicion_ocupacional", "Por posición ocupacional", {})],
                  [("lugar_trabajo", "Por lugar de trabajo", {})]]),
    ("Sector", [[("sector_economico_seccion", "Por sector económico", {})]]),
    ("Oficio", [[("oficio_gran_grupo", "Por oficio", {})]]),
]


def bloque_graficos(df, fn):
    tabs = st.tabs([g[0] for g in GRUPOS])
    for tab, (_, filas) in zip(tabs, GRUPOS):
        with tab:
            for fila in filas:
                cols = st.columns(len(fila), gap="large")
                for col, (dim, tit, opts) in zip(cols, fila):
                    with col:
                        fn(df, dim, tit, **opts)


# ---------------------------------------------------------------------------
# COMPONENTES DE INTERFAZ
# ---------------------------------------------------------------------------
def kpi(valor, etiqueta, clase):
    st.markdown(f'<div class="kpi-v {clase}">{valor}</div><div class="kpi-l">{etiqueta}</div>',
                unsafe_allow_html=True)


def ir(pagina):
    st.session_state.page = pagina


NAV = [("inicio", "Inicio"), ("formalidad", "Formalidad"), ("ingresos", "Ingresos"),
       ("salario", "Salarios"), ("empleo", "Empleo")]


def barra_nav():
    with st.container(key="nav"):
        marca, *botones = st.columns([5, 1, 1.3, 1.1, 1.1, 1.1], vertical_alignment="center")
        marca.markdown('<div class="brand">Mercado laboral</div>', unsafe_allow_html=True)
        for col, (k, etiqueta) in zip(botones, NAV):
            col.button(etiqueta, key=f"nav_{k}", on_click=ir, args=(k,),
                       type="primary" if st.session_state.page == k else "secondary")
    st.markdown('<hr class="rule">', unsafe_allow_html=True)


FILTROS = [("anio", "Año"), ("Mes Letras", "Mes"), ("departamento", "Departamento"),
           ("sexo", "Sexo"), ("nivel_educativo", "Educación")]


def barra_filtros(df_raw, clave):
    """Filtros horizontales; vacío = Todos. Devuelve el DataFrame filtrado."""
    sel = {}
    with st.container(key="filters"):
        for col, (c, etiqueta) in zip(st.columns(len(FILTROS), gap="medium"), FILTROS):
            opciones = MESES_ORDEN if c == "Mes Letras" else sorted(df_raw[c].dropna().unique().tolist(), key=str)
            sel[c] = col.multiselect(etiqueta, opciones, placeholder="Todos", key=f"f_{clave}_{c}")
        df = df_raw
        for c, valores in sel.items():
            if valores:
                df = df[df[c].isin(valores)]
        st.markdown(f'<div class="aux">{fmt_n(len(df))} registros seleccionados de {fmt_n(len(df_raw))}</div>',
                    unsafe_allow_html=True)
    return df


def encabezado(titulo, subtitulo):
    st.markdown(f'<div class="page-title">{titulo}</div><div class="page-sub">{subtitulo}</div>',
                unsafe_allow_html=True)


def pie():
    st.markdown('<div class="foot">Fuente: Gran Encuesta Integrada de Hogares (GEIH), DANE.</div>',
                unsafe_allow_html=True)


BIENVENIDA = {"role": "assistant", "content": "Hola. Estoy en desarrollo, pero pronto podré responder "
              "tus preguntas sobre los datos de cada sección."}
SUGERENCIAS = {
    "formalidad": ["¿Qué departamento tiene mayor formalidad?",
                   "¿Cómo cambia la formalidad según el nivel educativo?",
                   "¿Cuál es el porcentaje de trabajo formal?"],
    "ingresos": ["¿Qué diferencia hay entre promedio y mediana?",
                 "¿Cómo ha cambiado el ingreso por año?",
                 "¿Qué sector tiene mayor ingreso promedio?"],
}
SUGERENCIAS_BASE = ["¿Qué datos puedo consultar aquí?", "¿Qué significa trabajo formal?"]


def responder(pregunta, pagina):
    """Punto de integración del asistente: reemplazar por la llamada al modelo."""
    return ("Todavía no puedo responder preguntas. Estoy en desarrollo y pronto podré "
            "ayudarte a interpretar los datos de esta sección.")


def enviar(pregunta):
    st.session_state.chat += [
        {"role": "user", "content": pregunta},
        {"role": "assistant", "content": responder(pregunta, st.session_state.page)},
    ]


def reiniciar_chat():
    st.session_state.chat = [BIENVENIDA]


def asistente():
    """Chatbot fijo y desplegado en todas las secciones."""
    if "chat" not in st.session_state:
        st.session_state.chat = [BIENVENIDA]
    with st.container(key="chat"):
        st.markdown('<div class="chat-title">Asistente virtual<span class="tag">En desarrollo</span></div>'
                    '<div class="chat-sub">Pregunta sobre los datos de esta sección.</div>',
                    unsafe_allow_html=True)
        mensajes = st.container(height=320, border=False)
        if len(st.session_state.chat) == 1:
            for i, q in enumerate(SUGERENCIAS.get(st.session_state.page, SUGERENCIAS_BASE)):
                with st.container(key=f"sug_{i}"):
                    st.button(q, key=f"sug_btn_{i}", on_click=enviar, args=(q,))
        pregunta = st.chat_input("Escribe tu pregunta", key="chat_input")
        if pregunta:
            enviar(pregunta)
        if len(st.session_state.chat) > 1:
            with st.container(key="chat_reset"):
                st.button("Nueva conversación", key="chat_reset_btn", on_click=reiniciar_chat)
        with mensajes:
            for m in st.session_state.chat:
                avatar = ":material/smart_toy:" if m["role"] == "assistant" else ":material/person:"
                st.chat_message(m["role"], avatar=avatar).write(m["content"])


# ---------------------------------------------------------------------------
# PÁGINAS
# ---------------------------------------------------------------------------
def pagina_inicio():
    """Portada: pantalla separada, sin navegación ni asistente."""
    st.html(MAPA_SVG)
    st.markdown(
        '<div class="cover-content">'
        '<div class="cover-eyebrow">Estadística descriptiva · GEIH</div>'
        '<div class="cover-title">Mercado laboral<br>en Colombia</div>'
        '<div class="cover-sub">Una solución para tomar decisiones sobre el empleo</div>'
        '</div>'
        '<div class="cover-foot">Fuente: Gran Encuesta Integrada de Hogares (GEIH), DANE.</div>',
        unsafe_allow_html=True)
    _, centro, _ = st.columns([1, 0.45, 1])
    with centro, st.container(key="cover_cta"):
        st.button("Iniciar", key="cover_go", on_click=ir, args=("formalidad",))


def pagina_formalidad(df_raw):
    cabecera = st.container()
    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    df = barra_filtros(df_raw, "formalidad")
    pf, pnf = pct_formal_no_formal(df)
    with cabecera, st.container(key="kpis"):
        c0, c1, c2 = st.columns([1.6, 1, 1], gap="large", vertical_alignment="center")
        with c0: encabezado("Formalidad laboral", "Proporción de personas ocupadas con empleo formal y no formal.")
        with c1: kpi(fmt_pct(pf), "Trabajo formal", "k-primary")
        with c2: kpi(fmt_pct(pnf), "Trabajo no formal", "k-teal")
    bloque_graficos(df, grafico_formalidad)
    pie()


def pagina_ingresos(df_raw):
    cabecera = st.container()
    st.markdown('<hr class="rule">', unsafe_allow_html=True)
    df = barra_filtros(df_raw, "ingresos")
    prom, med = promedio_mediana_ingreso(df)
    with cabecera, st.container(key="kpis"):
        c0, c1, c2 = st.columns([1.6, 1, 1], gap="large", vertical_alignment="center")
        with c0: encabezado("Ingresos", "Promedio y mediana del ingreso laboral total.")
        with c1: kpi(fmt_cop(prom), "Ingreso promedio", "k-primary")
        with c2: kpi(fmt_cop(med), "Mediana", "k-accent")
    bloque_graficos(df, grafico_ingreso)
    pie()


def pagina_vacia(titulo, subtitulo):
    encabezado(titulo, subtitulo)
    st.markdown('<div class="canvas-empty">Esta sección está en desarrollo</div>', unsafe_allow_html=True)
    pie()


# ---------------------------------------------------------------------------
# APP
# ---------------------------------------------------------------------------
inject_css()
if "page" not in st.session_state:
    st.session_state.page = "inicio"

df_raw = load_data(DATA_PATH)
if st.session_state.page != "inicio":
    barra_nav()

pagina = st.session_state.page
if pagina == "inicio":
    pagina_inicio()
elif pagina == "formalidad":
    pagina_formalidad(df_raw)
elif pagina == "ingresos":
    pagina_ingresos(df_raw)
elif pagina == "salario":
    pagina_vacia("Proyección de salario", "Estimación del ingreso laboral según el perfil de la persona.")
else:
    pagina_vacia("Probabilidad de empleo formal", "Estimación de la probabilidad de conseguir un empleo formal.")

if pagina != "inicio":
    asistente()

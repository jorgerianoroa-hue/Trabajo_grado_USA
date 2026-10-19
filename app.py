"""
Mercado laboral de Colombia (GEIH): análisis descriptivo.
Ejecutar con:  streamlit run app.py
"""

import base64
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
MAPA_SVG = '<svg class="cover-map" viewBox="0 0 1371 1834" preserveAspectRatio="xMidYMid meet" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><path d="M179 0V1834M379 0V1834M579 0V1834M779 0V1834M979 0V1834M1179 0V1834M0 1724H1371M0 1524H1371M0 1324H1371M0 1124H1371M0 924H1371M0 724H1371M0 524H1371M0 324H1371M0 124H1371" fill="none" stroke="#164E63" stroke-opacity=".12" stroke-width="1" stroke-dasharray="2 8"/><path d="M172 1724h14M179 1717v14M172 1524h14M179 1517v14M172 1324h14M179 1317v14M172 1124h14M179 1117v14M172 924h14M179 917v14M172 724h14M179 717v14M172 524h14M179 517v14M172 324h14M179 317v14M172 124h14M179 117v14M372 1724h14M379 1717v14M372 1524h14M379 1517v14M372 1324h14M379 1317v14M372 1124h14M379 1117v14M372 924h14M379 917v14M372 724h14M379 717v14M372 524h14M379 517v14M372 324h14M379 317v14M372 124h14M379 117v14M572 1724h14M579 1717v14M572 1524h14M579 1517v14M572 1324h14M579 1317v14M572 1124h14M579 1117v14M572 924h14M579 917v14M572 724h14M579 717v14M572 524h14M579 517v14M572 324h14M579 317v14M572 124h14M579 117v14M772 1724h14M779 1717v14M772 1524h14M779 1517v14M772 1324h14M779 1317v14M772 1124h14M779 1117v14M772 924h14M779 917v14M772 724h14M779 717v14M772 524h14M779 517v14M772 324h14M779 317v14M772 124h14M779 117v14M972 1724h14M979 1717v14M972 1524h14M979 1517v14M972 1324h14M979 1317v14M972 1124h14M979 1117v14M972 924h14M979 917v14M972 724h14M979 717v14M972 524h14M979 517v14M972 324h14M979 317v14M972 124h14M979 117v14M1172 1724h14M1179 1717v14M1172 1524h14M1179 1517v14M1172 1324h14M1179 1317v14M1172 1124h14M1179 1117v14M1172 924h14M1179 917v14M1172 724h14M1179 717v14M1172 524h14M1179 517v14M1172 324h14M1179 317v14M1172 124h14M1179 117v14" fill="none" stroke="#164E63" stroke-opacity=".3" stroke-width="1.5"/><text x="8" y="1717" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">4°S</text><text x="8" y="1517" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">2°S</text><text x="8" y="1317" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">0°</text><text x="8" y="1117" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">2°N</text><text x="8" y="917" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">4°N</text><text x="8" y="717" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">6°N</text><text x="8" y="517" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">8°N</text><text x="8" y="317" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">10°N</text><text x="8" y="117" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">12°N</text><text x="185" y="1826" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">78°O</text><text x="385" y="1826" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">76°O</text><text x="585" y="1826" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">74°O</text><text x="785" y="1826" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">72°O</text><text x="985" y="1826" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">70°O</text><text x="1185" y="1826" fill="#64748B" fill-opacity=".85" font-family="Inter,sans-serif" font-size="16">68°O</text><path d="M442 1339L399 1315L350 1282L321 1298L237 1284L212 1241L194 1243L94 1186L80 1155L117 1147L113 1097L136 1061L186 1054L228 991L266 939L229 915L248 857L226 765L247 739L231 655L191 601L204 553L236 560L255 530L232 471L244 457L295 460L370 390L412 379L413 346L431 262L488 215L551 214L559 193L638 201L716 151L755 128L804 80L839 86L865 112L846 146L782 163L756 213L718 242L689 279L676 350L649 409L700 415L713 461L735 483L743 523L731 560L735 581L759 590L783 625L912 615L970 628L1040 714L1081 703L1153 708L1210 697L1245 714L1227 768L1205 802L1197 873L1217 940L1245 969L1249 992L1198 1042L1234 1064L1261 1099L1291 1198L1273 1211L1253 1152L1225 1120L1192 1154L997 1152L999 1215L1057 1225L1054 1263L1034 1253L978 1270L977 1342L1021 1379L1037 1436L1035 1479L990 1754L940 1700L910 1698L974 1596L898 1549L838 1558L802 1541L747 1567L672 1555L613 1450L567 1424L535 1377L468 1329L442 1339Z" fill="#164E63" fill-opacity=".035" stroke="#164E63" stroke-opacity=".4" stroke-width="2" stroke-linejoin="round"/><path d="M944 1566h0M971 1566h0M768 1543h0M849 1543h0M876 1543h0M903 1543h0M930 1543h0M957 1543h0M782 1520h0M809 1520h0M836 1520h0M863 1520h0M890 1520h0M917 1520h0M944 1520h0M971 1520h0M795 1496h0M822 1496h0M849 1496h0M876 1496h0M903 1496h0M930 1496h0M809 1473h0M836 1473h0M863 1473h0M890 1473h0M917 1473h0M822 1450h0M849 1450h0M876 1450h0M903 1450h0M836 1426h0M863 1426h0M890 1426h0M822 1403h0M849 1403h0M876 1403h0M836 1379h0M863 1379h0M890 1379h0M822 1356h0M849 1356h0M876 1356h0M809 1333h0M836 1333h0M863 1333h0M890 1333h0M795 1309h0M822 1309h0M849 1309h0M876 1309h0M903 1309h0M782 1286h0M809 1286h0M836 1286h0M863 1286h0M890 1286h0M768 1263h0M795 1263h0M822 1263h0M849 1263h0M876 1263h0M903 1263h0M755 1239h0M782 1239h0M809 1239h0M836 1239h0M863 1239h0M890 1239h0M917 1239h0M714 1216h0M741 1216h0M768 1216h0M795 1216h0M822 1216h0M849 1216h0M876 1216h0M903 1216h0M930 1216h0M701 1192h0M728 1192h0M755 1192h0M782 1192h0M809 1192h0M836 1192h0M863 1192h0M890 1192h0M917 1192h0M944 1192h0M687 1169h0M714 1169h0M741 1169h0M768 1169h0M795 1169h0M822 1169h0M849 1169h0M876 1169h0M903 1169h0M930 1169h0M957 1169h0M674 1146h0M701 1146h0M728 1146h0M755 1146h0M782 1146h0M809 1146h0M836 1146h0M863 1146h0M890 1146h0M917 1146h0M944 1146h0M282 1122h0M309 1122h0M336 1122h0M363 1122h0M633 1122h0M660 1122h0M687 1122h0M714 1122h0M741 1122h0M768 1122h0M795 1122h0M822 1122h0M849 1122h0M876 1122h0M903 1122h0M930 1122h0M957 1122h0M269 1099h0M296 1099h0M323 1099h0M350 1099h0M377 1099h0M404 1099h0M620 1099h0M647 1099h0M674 1099h0M701 1099h0M728 1099h0M755 1099h0M782 1099h0M809 1099h0M836 1099h0M863 1099h0M890 1099h0M917 1099h0M944 1099h0M971 1099h0M255 1075h0M282 1075h0M309 1075h0M336 1075h0M363 1075h0M390 1075h0M417 1075h0M444 1075h0M471 1075h0M579 1075h0M606 1075h0M633 1075h0M660 1075h0M687 1075h0M714 1075h0M741 1075h0M768 1075h0M795 1075h0M822 1075h0M849 1075h0M876 1075h0M903 1075h0M930 1075h0M957 1075h0M242 1052h0M269 1052h0M296 1052h0M323 1052h0M350 1052h0M377 1052h0M404 1052h0M431 1052h0M458 1052h0M485 1052h0M512 1052h0M539 1052h0M566 1052h0M593 1052h0M620 1052h0M647 1052h0M674 1052h0M701 1052h0M728 1052h0M755 1052h0M782 1052h0M809 1052h0M836 1052h0M863 1052h0M890 1052h0M917 1052h0M944 1052h0M971 1052h0M228 1029h0M255 1029h0M282 1029h0M309 1029h0M336 1029h0M363 1029h0M390 1029h0M417 1029h0M444 1029h0M471 1029h0M498 1029h0M525 1029h0M552 1029h0M579 1029h0M606 1029h0M633 1029h0M660 1029h0M687 1029h0M714 1029h0M741 1029h0M768 1029h0M795 1029h0M822 1029h0M849 1029h0M876 1029h0M903 1029h0M930 1029h0M957 1029h0M242 1005h0M269 1005h0M296 1005h0M323 1005h0M350 1005h0M377 1005h0M404 1005h0M431 1005h0M458 1005h0M485 1005h0M512 1005h0M539 1005h0M566 1005h0M593 1005h0M620 1005h0M647 1005h0M674 1005h0M701 1005h0M728 1005h0M755 1005h0M782 1005h0M809 1005h0M836 1005h0M863 1005h0M890 1005h0M917 1005h0M944 1005h0M255 982h0M282 982h0M309 982h0M336 982h0M363 982h0M390 982h0M417 982h0M444 982h0M471 982h0M498 982h0M525 982h0M552 982h0M579 982h0M606 982h0M633 982h0M660 982h0M687 982h0M714 982h0M741 982h0M768 982h0M795 982h0M822 982h0M849 982h0M876 982h0M903 982h0M930 982h0M1227 982h0M269 959h0M296 959h0M323 959h0M350 959h0M377 959h0M404 959h0M431 959h0M458 959h0M485 959h0M512 959h0M539 959h0M566 959h0M593 959h0M620 959h0M647 959h0M674 959h0M701 959h0M728 959h0M755 959h0M782 959h0M809 959h0M836 959h0M863 959h0M890 959h0M917 959h0M282 935h0M309 935h0M336 935h0M363 935h0M390 935h0M417 935h0M444 935h0M471 935h0M498 935h0M525 935h0M552 935h0M579 935h0M606 935h0M633 935h0M660 935h0M687 935h0M714 935h0M741 935h0M768 935h0M795 935h0M822 935h0M849 935h0M876 935h0M903 935h0M242 912h0M269 912h0M296 912h0M323 912h0M350 912h0M377 912h0M404 912h0M431 912h0M458 912h0M485 912h0M512 912h0M539 912h0M593 912h0M620 912h0M647 912h0M674 912h0M701 912h0M728 912h0M755 912h0M782 912h0M809 912h0M836 912h0M863 912h0M890 912h0M255 888h0M282 888h0M309 888h0M336 888h0M363 888h0M390 888h0M417 888h0M444 888h0M471 888h0M498 888h0M660 888h0M687 888h0M714 888h0M741 888h0M768 888h0M795 888h0M822 888h0M849 888h0M269 865h0M296 865h0M323 865h0M350 865h0M377 865h0M404 865h0M431 865h0M458 865h0M728 865h0M755 865h0M782 865h0M809 865h0M255 842h0M282 842h0M309 842h0M336 842h0M363 842h0M390 842h0M417 842h0M444 842h0M269 818h0M296 818h0M323 818h0M350 818h0M377 818h0M404 818h0M431 818h0M282 795h0M309 795h0M336 795h0M363 795h0M390 795h0M417 795h0M269 772h0M296 772h0M323 772h0M350 772h0M377 772h0M404 772h0M282 748h0M309 748h0M336 748h0M363 748h0M390 748h0M269 725h0M296 725h0M323 725h0M350 725h0M377 725h0M404 725h0M255 701h0M282 701h0M309 701h0M336 701h0M363 701h0M390 701h0M269 678h0M296 678h0M323 678h0M350 678h0M377 678h0M404 678h0M255 655h0M282 655h0M309 655h0M336 655h0M363 655h0M390 655h0M242 631h0M269 631h0M296 631h0M323 631h0M350 631h0M377 631h0M404 631h0M228 608h0M255 608h0M282 608h0M309 608h0M336 608h0M363 608h0M390 608h0M417 608h0M215 584h0M242 584h0M269 584h0M296 584h0M323 584h0M350 584h0M377 584h0M404 584h0M255 561h0M282 561h0M309 561h0M336 561h0M363 561h0M390 561h0M417 561h0M269 538h0M296 538h0M323 538h0M350 538h0M377 538h0M404 538h0M431 538h0M282 514h0M309 514h0M336 514h0M363 514h0M390 514h0M417 514h0M269 491h0M296 491h0M323 491h0M350 491h0M377 491h0M404 491h0M431 491h0M728 491h0M255 468h0M282 468h0M309 468h0M336 468h0M363 468h0M390 468h0M417 468h0M323 444h0M350 444h0M377 444h0M404 444h0M431 444h0M701 444h0M363 421h0M390 421h0M417 421h0M377 397h0M404 397h0M714 234h0M728 210h0M741 187h0M728 164h0M755 164h0M768 140h0M795 140h0M822 140h0M782 117h0M809 117h0M836 117h0M822 93h0" fill="none" stroke="#164E63" stroke-opacity=".16" stroke-width="6" stroke-linecap="round"/><path d="M971 1707h0M930 1683h0M957 1683h0M984 1683h0M944 1660h0M971 1660h0M957 1637h0M984 1637h0M998 1613h0M984 1590h0M998 1566h0M687 1543h0M714 1543h0M741 1543h0M984 1543h0M1011 1543h0M674 1520h0M701 1520h0M728 1520h0M755 1520h0M998 1520h0M687 1496h0M714 1496h0M741 1496h0M768 1496h0M957 1496h0M984 1496h0M1011 1496h0M701 1473h0M728 1473h0M755 1473h0M782 1473h0M944 1473h0M971 1473h0M998 1473h0M1025 1473h0M714 1450h0M741 1450h0M768 1450h0M795 1450h0M930 1450h0M957 1450h0M984 1450h0M1011 1450h0M728 1426h0M755 1426h0M782 1426h0M809 1426h0M917 1426h0M944 1426h0M971 1426h0M998 1426h0M1025 1426h0M741 1403h0M768 1403h0M795 1403h0M903 1403h0M930 1403h0M957 1403h0M984 1403h0M1011 1403h0M728 1379h0M755 1379h0M782 1379h0M809 1379h0M917 1379h0M944 1379h0M971 1379h0M998 1379h0M741 1356h0M768 1356h0M795 1356h0M903 1356h0M930 1356h0M957 1356h0M728 1333h0M755 1333h0M782 1333h0M917 1333h0M944 1333h0M714 1309h0M741 1309h0M768 1309h0M930 1309h0M957 1309h0M296 1286h0M323 1286h0M701 1286h0M728 1286h0M755 1286h0M917 1286h0M944 1286h0M255 1263h0M282 1263h0M309 1263h0M336 1263h0M687 1263h0M714 1263h0M741 1263h0M930 1263h0M957 1263h0M242 1239h0M269 1239h0M296 1239h0M323 1239h0M350 1239h0M674 1239h0M701 1239h0M728 1239h0M944 1239h0M971 1239h0M998 1239h0M1025 1239h0M174 1216h0M201 1216h0M228 1216h0M255 1216h0M282 1216h0M309 1216h0M336 1216h0M363 1216h0M390 1216h0M660 1216h0M687 1216h0M957 1216h0M984 1216h0M161 1192h0M188 1192h0M215 1192h0M242 1192h0M269 1192h0M296 1192h0M323 1192h0M350 1192h0M377 1192h0M404 1192h0M620 1192h0M647 1192h0M674 1192h0M971 1192h0M120 1169h0M147 1169h0M174 1169h0M201 1169h0M228 1169h0M255 1169h0M282 1169h0M309 1169h0M336 1169h0M363 1169h0M390 1169h0M417 1169h0M444 1169h0M579 1169h0M606 1169h0M633 1169h0M660 1169h0M984 1169h0M134 1146h0M161 1146h0M188 1146h0M215 1146h0M242 1146h0M269 1146h0M296 1146h0M323 1146h0M350 1146h0M377 1146h0M404 1146h0M431 1146h0M458 1146h0M485 1146h0M512 1146h0M539 1146h0M566 1146h0M593 1146h0M620 1146h0M647 1146h0M971 1146h0M1052 1146h0M1160 1146h0M1187 1146h0M1268 1146h0M147 1122h0M174 1122h0M201 1122h0M228 1122h0M255 1122h0M390 1122h0M417 1122h0M444 1122h0M471 1122h0M498 1122h0M525 1122h0M552 1122h0M579 1122h0M606 1122h0M984 1122h0M1011 1122h0M1038 1122h0M1065 1122h0M1146 1122h0M1173 1122h0M1200 1122h0M1254 1122h0M134 1099h0M161 1099h0M188 1099h0M215 1099h0M242 1099h0M431 1099h0M458 1099h0M485 1099h0M512 1099h0M539 1099h0M566 1099h0M593 1099h0M998 1099h0M1025 1099h0M1052 1099h0M1079 1099h0M1106 1099h0M1133 1099h0M1160 1099h0M1187 1099h0M1214 1099h0M1241 1099h0M147 1075h0M174 1075h0M201 1075h0M228 1075h0M498 1075h0M525 1075h0M552 1075h0M984 1075h0M1011 1075h0M1038 1075h0M1065 1075h0M1092 1075h0M1119 1075h0M1146 1075h0M1173 1075h0M1200 1075h0M1227 1075h0M215 1052h0M998 1052h0M1025 1052h0M1052 1052h0M1079 1052h0M1106 1052h0M1133 1052h0M1160 1052h0M1187 1052h0M984 1029h0M1011 1029h0M1038 1029h0M1065 1029h0M1092 1029h0M1119 1029h0M1146 1029h0M1173 1029h0M1200 1029h0M971 1005h0M998 1005h0M1025 1005h0M1052 1005h0M1106 1005h0M1133 1005h0M1160 1005h0M1187 1005h0M1214 1005h0M957 982h0M984 982h0M1011 982h0M1119 982h0M1146 982h0M1173 982h0M1200 982h0M944 959h0M971 959h0M998 959h0M1133 959h0M1160 959h0M1187 959h0M1214 959h0M930 935h0M957 935h0M984 935h0M1146 935h0M1173 935h0M1200 935h0M566 912h0M917 912h0M944 912h0M971 912h0M1160 912h0M1187 912h0M525 888h0M552 888h0M579 888h0M606 888h0M633 888h0M876 888h0M903 888h0M930 888h0M1173 888h0M485 865h0M512 865h0M539 865h0M566 865h0M593 865h0M620 865h0M647 865h0M674 865h0M701 865h0M836 865h0M863 865h0M890 865h0M917 865h0M1187 865h0M471 842h0M498 842h0M525 842h0M552 842h0M579 842h0M606 842h0M633 842h0M660 842h0M687 842h0M714 842h0M741 842h0M768 842h0M795 842h0M822 842h0M849 842h0M876 842h0M903 842h0M1173 842h0M458 818h0M485 818h0M512 818h0M539 818h0M566 818h0M593 818h0M620 818h0M647 818h0M674 818h0M701 818h0M728 818h0M755 818h0M782 818h0M809 818h0M836 818h0M863 818h0M890 818h0M1187 818h0M255 795h0M444 795h0M471 795h0M498 795h0M525 795h0M687 795h0M714 795h0M741 795h0M768 795h0M795 795h0M822 795h0M849 795h0M1200 795h0M242 772h0M431 772h0M458 772h0M485 772h0M512 772h0M728 772h0M755 772h0M782 772h0M809 772h0M836 772h0M1187 772h0M1214 772h0M255 748h0M417 748h0M444 748h0M471 748h0M498 748h0M768 748h0M795 748h0M1173 748h0M1200 748h0M431 725h0M458 725h0M485 725h0M1187 725h0M1214 725h0M417 701h0M444 701h0M471 701h0M431 678h0M458 678h0M809 678h0M836 678h0M417 655h0M444 655h0M471 655h0M795 655h0M822 655h0M849 655h0M876 655h0M431 631h0M458 631h0M485 631h0M755 631h0M809 631h0M836 631h0M863 631h0M890 631h0M917 631h0M444 608h0M471 608h0M741 608h0M431 584h0M458 584h0M485 584h0M728 584h0M444 561h0M471 561h0M498 561h0M687 561h0M714 561h0M458 538h0M485 538h0M674 538h0M701 538h0M728 538h0M444 514h0M471 514h0M498 514h0M660 514h0M687 514h0M714 514h0M458 491h0M485 491h0M512 491h0M647 491h0M674 491h0M701 491h0M444 468h0M471 468h0M498 468h0M525 468h0M633 468h0M660 468h0M687 468h0M458 444h0M485 444h0M512 444h0M620 444h0M647 444h0M674 444h0M444 421h0M471 421h0M498 421h0M525 421h0M606 421h0M633 421h0M660 421h0M687 421h0M431 397h0M458 397h0M485 397h0M512 397h0M593 397h0M620 397h0M444 374h0M471 374h0M498 374h0M606 374h0M633 374h0M431 351h0M458 351h0M485 351h0M620 351h0M647 351h0M444 327h0M471 327h0M633 327h0M660 327h0M431 304h0M620 304h0M647 304h0M674 304h0M633 280h0M660 280h0M647 257h0M674 257h0M660 234h0M687 234h0M647 210h0M674 210h0M701 210h0M687 187h0M714 187h0" fill="none" stroke="#164E63" stroke-opacity=".24" stroke-width="10" stroke-linecap="round"/><path d="M984 1730h0M660 1496h0M647 1473h0M674 1473h0M633 1450h0M660 1450h0M687 1450h0M593 1426h0M620 1426h0M647 1426h0M674 1426h0M701 1426h0M579 1403h0M606 1403h0M633 1403h0M660 1403h0M687 1403h0M714 1403h0M566 1379h0M593 1379h0M620 1379h0M647 1379h0M674 1379h0M701 1379h0M525 1356h0M552 1356h0M579 1356h0M606 1356h0M633 1356h0M660 1356h0M687 1356h0M714 1356h0M512 1333h0M539 1333h0M566 1333h0M593 1333h0M620 1333h0M647 1333h0M674 1333h0M701 1333h0M417 1309h0M444 1309h0M471 1309h0M498 1309h0M525 1309h0M552 1309h0M579 1309h0M606 1309h0M633 1309h0M660 1309h0M687 1309h0M377 1286h0M404 1286h0M431 1286h0M458 1286h0M485 1286h0M512 1286h0M539 1286h0M566 1286h0M593 1286h0M620 1286h0M647 1286h0M674 1286h0M363 1263h0M390 1263h0M417 1263h0M444 1263h0M471 1263h0M498 1263h0M525 1263h0M552 1263h0M579 1263h0M606 1263h0M633 1263h0M660 1263h0M377 1239h0M404 1239h0M431 1239h0M458 1239h0M485 1239h0M512 1239h0M539 1239h0M566 1239h0M593 1239h0M620 1239h0M647 1239h0M417 1216h0M444 1216h0M471 1216h0M498 1216h0M525 1216h0M552 1216h0M579 1216h0M606 1216h0M633 1216h0M134 1192h0M431 1192h0M458 1192h0M485 1192h0M512 1192h0M539 1192h0M566 1192h0M593 1192h0M471 1169h0M498 1169h0M525 1169h0M552 1169h0M1079 1146h0M1106 1146h0M1133 1146h0M1092 1122h0M1119 1122h0M1079 1005h0M1038 982h0M1065 982h0M1092 982h0M1025 959h0M1052 959h0M1079 959h0M1106 959h0M1011 935h0M1038 935h0M1065 935h0M1092 935h0M1119 935h0M998 912h0M1025 912h0M1052 912h0M1079 912h0M1106 912h0M1133 912h0M957 888h0M984 888h0M1011 888h0M1038 888h0M1065 888h0M1092 888h0M1119 888h0M1146 888h0M944 865h0M971 865h0M998 865h0M1025 865h0M1052 865h0M1079 865h0M1106 865h0M1133 865h0M1160 865h0M930 842h0M957 842h0M984 842h0M1011 842h0M1038 842h0M1065 842h0M1092 842h0M1119 842h0M1146 842h0M917 818h0M944 818h0M971 818h0M998 818h0M1025 818h0M1052 818h0M1079 818h0M1106 818h0M1133 818h0M1160 818h0M552 795h0M579 795h0M606 795h0M633 795h0M660 795h0M876 795h0M903 795h0M930 795h0M957 795h0M984 795h0M1011 795h0M1038 795h0M1065 795h0M1092 795h0M1119 795h0M1146 795h0M1173 795h0M539 772h0M566 772h0M593 772h0M620 772h0M647 772h0M674 772h0M701 772h0M863 772h0M890 772h0M917 772h0M944 772h0M971 772h0M998 772h0M1025 772h0M1052 772h0M1079 772h0M1106 772h0M1133 772h0M1160 772h0M525 748h0M552 748h0M579 748h0M606 748h0M633 748h0M660 748h0M687 748h0M714 748h0M741 748h0M822 748h0M849 748h0M876 748h0M903 748h0M930 748h0M957 748h0M984 748h0M1011 748h0M1038 748h0M1065 748h0M1092 748h0M1119 748h0M1146 748h0M512 725h0M539 725h0M566 725h0M593 725h0M620 725h0M647 725h0M674 725h0M701 725h0M728 725h0M755 725h0M782 725h0M809 725h0M836 725h0M863 725h0M890 725h0M917 725h0M944 725h0M971 725h0M998 725h0M1025 725h0M1052 725h0M1079 725h0M1106 725h0M1133 725h0M1160 725h0M498 701h0M525 701h0M552 701h0M579 701h0M606 701h0M633 701h0M660 701h0M687 701h0M714 701h0M741 701h0M768 701h0M795 701h0M822 701h0M849 701h0M876 701h0M903 701h0M930 701h0M957 701h0M984 701h0M1011 701h0M485 678h0M512 678h0M539 678h0M566 678h0M593 678h0M620 678h0M647 678h0M674 678h0M701 678h0M728 678h0M755 678h0M782 678h0M863 678h0M890 678h0M917 678h0M944 678h0M971 678h0M998 678h0M498 655h0M525 655h0M552 655h0M579 655h0M606 655h0M633 655h0M660 655h0M687 655h0M714 655h0M741 655h0M768 655h0M903 655h0M930 655h0M957 655h0M512 631h0M539 631h0M566 631h0M593 631h0M620 631h0M647 631h0M674 631h0M701 631h0M728 631h0M944 631h0M498 608h0M525 608h0M552 608h0M579 608h0M606 608h0M633 608h0M660 608h0M687 608h0M714 608h0M512 584h0M539 584h0M566 584h0M593 584h0M620 584h0M647 584h0M674 584h0M701 584h0M525 561h0M552 561h0M579 561h0M606 561h0M633 561h0M660 561h0M512 538h0M539 538h0M566 538h0M593 538h0M620 538h0M647 538h0M525 514h0M552 514h0M579 514h0M606 514h0M633 514h0M539 491h0M566 491h0M593 491h0M620 491h0M552 468h0M579 468h0M606 468h0M539 444h0M566 444h0M593 444h0M552 421h0M579 421h0M539 397h0M566 397h0M525 374h0M552 374h0M579 374h0M512 351h0M539 351h0M566 351h0M593 351h0M498 327h0M525 327h0M552 327h0M579 327h0M606 327h0M458 304h0M485 304h0M512 304h0M539 304h0M566 304h0M593 304h0M444 280h0M471 280h0M498 280h0M525 280h0M552 280h0M579 280h0M606 280h0M458 257h0M485 257h0M512 257h0M539 257h0M566 257h0M593 257h0M620 257h0M498 234h0M525 234h0M552 234h0M579 234h0M606 234h0M633 234h0M566 210h0M593 210h0M620 210h0" fill="none" stroke="#164E63" stroke-opacity=".34" stroke-width="15" stroke-linecap="round"/></svg>'
MAPA_URI = "data:image/svg+xml;base64," + base64.b64encode(MAPA_SVG.encode("utf-8")).decode()

CSS = Template("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Manrope:wght@500;600;700&display=swap');
html, body, [class*="css"], .stApp { font-family:'$F_BODY',sans-serif; color:$TEXT; }
.stApp { background:$BG; }
.block-container { max-width:1440px; padding:.8rem 2.4rem 2rem; }
header[data-testid="stHeader"] { background:transparent; }
footer { visibility:hidden; }
h1,h2,h3 { font-family:'$F_DISPLAY',sans-serif; }
[data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] p, .stButton button, .stButton button p,
.stTabs [data-baseweb="tab"] p, label, input, [data-baseweb="select"] { font-family:'$F_BODY',sans-serif !important; }

/* Navegación superior */
.brand { font-family:'$F_DISPLAY',sans-serif; font-weight:700; font-size:1.1rem; color:$PRIMARY; letter-spacing:-0.01em; padding-top:.3rem; }
.st-key-nav button { width:auto; min-height:0; padding:.35rem 0 .45rem; background:transparent; border:none;
    border-bottom:2px solid transparent; border-radius:0; color:$MUTED; font-weight:500; font-size:.88rem; white-space:nowrap;
    transition:color .15s, border-color .15s; }
.st-key-nav button:hover { color:$TEXT; background:transparent; border-bottom-color:$BORDER; }
.st-key-nav button[kind="primary"], .st-key-nav button[data-testid="stBaseButton-primary"],
.st-key-nav button[kind="primary"]:hover, .st-key-nav button[data-testid="stBaseButton-primary"]:hover {
    color:$PRIMARY; font-weight:600; border-bottom-color:$PRIMARY; background:transparent; }
.st-key-nav button p, div[class*="st-key-link_"] button p { color:inherit; font-size:inherit; font-weight:inherit; }

/* Disposición del menú: marca a la izquierda, secciones a la derecha */
.st-key-nav { flex-direction:row !important; flex-wrap:wrap; align-items:center; justify-content:space-between; gap:.3rem 2rem; }
.st-key-nav > * { width:auto !important; min-width:0; flex:0 0 auto; }
.st-key-nav > :last-child { flex:1 1 auto !important; }
.st-key-nav [data-testid="stHorizontalBlock"] { flex-wrap:nowrap; align-items:center; gap:1.4rem; }
.st-key-nav [data-testid="stColumn"] { flex:0 0 auto !important; width:auto !important; min-width:0 !important; }
.st-key-nav_brand [data-testid="stHorizontalBlock"] { gap:.4rem; }
.st-key-nav_items [data-testid="stHorizontalBlock"] { justify-content:flex-end; }
.st-key-nav .brand { white-space:nowrap; padding-top:0; }

/* Enlaces de texto (Explorar →) */
div[class*="st-key-link_"] button { width:auto; min-height:0; padding:0; background:transparent; border:none;
    color:$PRIMARY; font-weight:500; font-size:.95rem; justify-content:flex-start; transition:color .15s; }
div[class*="st-key-link_"] button:hover { color:$SECONDARY; background:transparent; text-decoration:underline; text-underline-offset:4px; }

/* Filtros compactos */
.st-key-filters label p { font-size:.78rem; color:$MUTED; font-weight:500; }
.st-key-filters [data-baseweb="select"] > div { background:$SURFACE !important; border:1px solid $BORDER; border-radius:8px; min-height:34px; font-size:.84rem; }
.st-key-filters [data-baseweb="tag"] { background:#E4EEF1; color:$PRIMARY; border-radius:6px; }
.aux { color:$MUTED; font-size:.8rem; text-align:right; }

/* Tipografía editorial */
.page-title { font-family:'$F_DISPLAY',sans-serif; font-size:1.6rem; font-weight:600; letter-spacing:-0.02em; }
.page-sub { color:$MUTED; font-size:.88rem; margin-top:.1rem; }
.tag { color:$ACCENT; font-size:.78rem; font-weight:500; border:1px solid $ACCENT; border-radius:999px; padding:0 .5rem; margin-left:.6rem; }
.chart-title { font-family:'$F_DISPLAY',sans-serif; font-size:.95rem; font-weight:600; margin:.9rem 0 0; }
.rule { border:none; border-top:1px solid $BORDER; margin:.4rem 0 .8rem; }
.foot { border-top:1px solid $BORDER; color:$MUTED; font-size:.82rem; margin-top:4rem; padding-top:1rem; }
.canvas-empty { min-height:460px; border:1px dashed $BORDER; border-radius:10px; display:flex; align-items:center; justify-content:center; color:$MUTED; font-size:.95rem; margin-top:1.5rem; }

/* KPIs: número grande + etiqueta + divisor vertical */
.kpi-v { font-family:'$F_BODY',sans-serif; font-size:2.4rem; font-weight:600; line-height:1.1; letter-spacing:-0.02em; font-variant-numeric:tabular-nums; }
.kpi-l { color:$MUTED; font-size:.88rem; margin-top:.2rem; }
.k-primary { color:$PRIMARY; } .k-teal { color:$SECONDARY; } .k-accent { color:$ACCENT; }
.st-key-kpis .kpi-v { font-size:1.9rem; } .st-key-kpis .kpi-l { font-size:.82rem; margin-top:0; }
.st-key-kpis [data-testid="stColumn"]:not(:first-child), .st-key-kpis [data-testid="column"]:not(:first-child) {
    border-left:1px solid $BORDER; padding-left:1.5rem; }

/* Tabs minimalistas */
.stTabs [data-baseweb="tab-list"] { gap:1.7rem; border-bottom:1px solid $BORDER; background:transparent; }
.stTabs [data-baseweb="tab"] { background:transparent; padding:.5rem 0; color:$MUTED; font-weight:500; font-size:.95rem; transition:color .15s; }
.stTabs [data-baseweb="tab"]:hover { color:$TEXT; background:transparent; }
.stTabs [aria-selected="true"] { color:$TEXT; font-weight:600; }
.stTabs [data-baseweb="tab-highlight"] { background:$PRIMARY; height:2px; }
.stTabs [data-baseweb="tab-border"] { background:transparent; }
.stTabs [data-baseweb="tab-panel"] { padding-top:.2rem; }

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

/* Portada: el mapa es el fondo de toda la app mientras se muestra la portada */
.stApp:has(.cover-content) { background-image:url("$MAPA_URI"); background-repeat:no-repeat;
    background-position:center; background-size:contain; }
.cover-content { text-align:center; padding-top:max(6vh, calc(50vh - 16rem)); }
.cover-title { font-family:'$F_DISPLAY',sans-serif; font-size:clamp(3rem, 7vw, 6.6rem); font-weight:600; line-height:1.02; letter-spacing:-0.035em;
    text-shadow:0 0 28px rgba(248,250,252,.95), 0 0 10px rgba(248,250,252,.95); }
.cover-sub { color:$MUTED; font-size:clamp(1.15rem, 1.7vw, 1.65rem); line-height:1.45; margin:1.5rem auto 0; max-width:680px;
    text-shadow:0 0 18px rgba(248,250,252,.95), 0 0 8px rgba(248,250,252,.95); }
.cover-foot { text-align:center; color:$MUTED; font-size:.82rem; margin-top:3.5rem; }
.st-key-cover_cta { display:flex; flex-direction:column; align-items:center; margin-top:2.4rem; }
.st-key-cover_cta button { min-width:240px; background:$PRIMARY; color:#FFFFFF; border:none; border-radius:8px;
    padding:1rem 2.6rem; transition:background .15s; }
.st-key-cover_cta button:hover { background:$SECONDARY; color:#FFFFFF; }
.st-key-cover_cta button p { color:inherit; font-size:1.15rem; font-weight:500; }

/* Ícono de inicio junto a la marca */
.st-key-nav_inicio button { color:$PRIMARY; }
.st-key-nav_inicio button:hover { color:$SECONDARY; }
.st-key-nav_inicio button p { display:none; }
.st-key-nav_inicio button span[data-testid="stIconMaterial"] { font-size:1.45rem; }

/* Secciones de modelos: variables, ejecución y resultados */
div[class*="st-key-panel_vars_"], div[class*="st-key-panel_result_"] { border:1px solid $BORDER; border-radius:10px; padding:1.5rem; }
div[class*="st-key-panel_vars_"] { background:$SURFACE; }
div[class*="st-key-panel_result_"] { border-style:dashed; min-height:660px; }
.step { display:flex; align-items:center; gap:.7rem; }
.step-n { display:inline-flex; align-items:center; justify-content:center; width:26px; height:26px; border-radius:50%;
    background:$PRIMARY; color:#FFFFFF; font-size:.82rem; font-weight:600; flex:none; }
.step-t { font-family:'$F_DISPLAY',sans-serif; font-size:1.15rem; font-weight:600; }
.step-sub { color:$MUTED; font-size:.9rem; line-height:1.5; margin:.35rem 0 .6rem; }
div[class*="st-key-panel_vars_"] label p { font-size:.82rem; color:$MUTED; font-weight:500; }
div[class*="st-key-panel_vars_"] [data-baseweb="select"] > div { border:1px solid $BORDER; border-radius:8px; background:$BG; }
div[class*="st-key-predecir_"] button { width:100%; background:$PRIMARY; color:#FFFFFF; border:none; border-radius:8px;
    padding:.85rem 1rem; font-size:1.05rem; font-weight:600; transition:background .15s; }
div[class*="st-key-predecir_"] button:hover { background:$SECONDARY; color:#FFFFFF; }
div[class*="st-key-predecir_"] button p { color:inherit; font-size:inherit; font-weight:inherit; }
.result-empty { min-height:420px; display:flex; align-items:center; justify-content:center; color:$MUTED;
    font-size:.95rem; border-top:1px solid $BORDER; margin-top:1rem; }
@media (min-width:1100px) { .block-container:has(.cover-content) { padding-right:2.4rem; } }
@media (max-width:900px) { .cover-title { font-size:2.8rem; } .cover-content { padding-top:12vh; } }

@media (max-width:900px) {
    .block-container { padding:1rem 1rem 2rem; }
    .st-key-nav_items [data-testid="stHorizontalBlock"] { flex-wrap:wrap; gap:.3rem 1.1rem; justify-content:flex-start; }
    .st-key-kpis [data-testid="stColumn"]:not(:first-child) { border-left:none; padding-left:0; }
}
</style>
""")


def inject_css():
    st.markdown(CSS.safe_substitute(
        F_BODY=F_BODY, F_DISPLAY=F_DISPLAY, TEXT=TEXT, BG=BG, SURFACE=SURFACE, MUTED=MUTED,
        PRIMARY=PRIMARY, SECONDARY=SECONDARY, ACCENT=ACCENT, BORDER=BORDER, MAPA_URI=MAPA_URI,
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


def estilizar_figura(fig, altura, pct, horizontal, apilado=False, margen_der=16, xmax=None):
    fig.update_layout(**PLOTLY_LAYOUT)
    fig.update_layout(height=altura, barmode="stack" if apilado else "group",
                      margin=dict(t=34, b=8, l=4, r=margen_der))
    valor = dict(showgrid=True, gridcolor=GRIDLINE, zeroline=False, showline=False,
                 tickfont=dict(size=11), tickformat=".0%" if pct else ",.0f",
                 tickprefix="" if pct else "$")
    if pct and horizontal:
        valor["range"] = [0, 1]
    elif xmax and horizontal:
        valor["range"] = [0, xmax]
    categoria = dict(showgrid=False, zeroline=False, showline=False, ticks="", type="category",
                     automargin=True, tickfont=dict(size=12, color=TEXT))
    if horizontal:
        fig.update_xaxes(**valor)
        fig.update_yaxes(**categoria)
    else:
        fig.update_yaxes(**valor)
        fig.update_xaxes(**categoria)
    return fig


def grafico_barras(d, dim, series, pct, apilado=False, marcador=None, key=None, xmax=None, altura=None, leyenda=True):
    """Barras horizontales (ranking). series: (nombre, columna, color, color_texto)."""
    cat = d[dim].astype(str)
    fmt, pre = ".1%" if pct else ",.0f", "" if pct else "$"
    fig = go.Figure()
    for nombre, col, color, txt in series:
        fig.add_bar(
            name=nombre, y=cat, x=d[col], orientation="h", marker=dict(color=color), showlegend=leyenda,
            customdata=d["n"], texttemplate=f"{pre}%{{x:{fmt}}}", cliponaxis=False,
            textposition="inside" if apilado else "outside", textfont=dict(color=txt, size=11),
            hovertemplate=f"<b>%{{y}}</b><br>{nombre}: {pre}%{{x:{fmt}}}<br>Registros: %{{customdata:,}}<extra></extra>",
        )
    if marcador:
        nombre, col, color = marcador
        fig.add_scatter(
            name=nombre, y=cat, x=d[col], mode="markers", customdata=d["n"], showlegend=leyenda,
            marker=dict(symbol="diamond", size=9, color=color, line=dict(color=SURFACE, width=1)),
            hovertemplate=f"<b>%{{y}}</b><br>{nombre}: {pre}%{{x:{fmt}}}<extra></extra>",
        )
    estilizar_figura(fig, altura or max(170, 24 * len(d) + 70), pct, True, apilado, margen_der=16 if pct else 70, xmax=xmax)
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
    estilizar_figura(fig, 300, pct, False, margen_der=40)
    st.plotly_chart(fig, config=PLOT_CONFIG, key=key)


def ranking(d, dim, series, pct, apilado=False, marcador=None, key=None, completo=False):
    """Ranking horizontal. Con ancho completo y muchas categorías se reparte en dos columnas (misma escala)."""
    cols = [s[1] for s in series] + ([marcador[1]] if marcador else [])
    xmax = None if pct else float(d[cols].max().max()) * 1.2
    if completo and len(d) > 16:
        k = (len(d) + 1) // 2
        alto = 24 * k + 70
        izq, der = st.columns(2, gap="large")
        with izq:  # d va de menor a mayor: la mitad alta queda a la izquierda
            grafico_barras(d.iloc[len(d) - k:], dim, series, pct, apilado, marcador, f"{key}_a", xmax, alto)
        with der:
            grafico_barras(d.iloc[:len(d) - k], dim, series, pct, apilado, marcador, f"{key}_b", xmax, alto, leyenda=False)
    else:
        grafico_barras(d, dim, series, pct, apilado, marcador, key, xmax)


def titulo_grafico(texto):
    st.markdown(f'<div class="chart-title">{texto}</div>', unsafe_allow_html=True)


def sin_datos():
    st.caption("No hay registros para los filtros seleccionados.")


def grafico_formalidad(df, dim, titulo, tendencia=False, completo=False):
    titulo_grafico(titulo)
    if df.empty:
        return sin_datos()
    d = agrupar(df, dim, "empleo_formal_pleno", ["mean"], por_n=not tendencia)
    d["no"] = 1 - d["mean"]
    series = [("Trabajo formal", "mean", PRIMARY, "#FFFFFF"), ("Trabajo no formal", "no", NOFORMAL, TEXT)]
    if tendencia:
        grafico_tendencia(d, dim, [s[:3] for s in series], True, key=f"ch_formalidad_{dim}")
    else:
        ranking(d.sort_values("mean"), dim, series, True, apilado=True, key=f"ch_formalidad_{dim}", completo=completo)


def grafico_ingreso(df, dim, titulo, tendencia=False, completo=False):
    titulo_grafico(titulo)
    if df.empty:
        return sin_datos()
    d = agrupar(df, dim, "ingreso_laboral_total", ["mean", "median"], por_n=not tendencia)
    if tendencia:
        grafico_tendencia(d, dim, [("Promedio", "mean", PRIMARY), ("Mediana", "median", ACCENT)],
                          False, key=f"ch_ingreso_{dim}")
    else:
        ranking(d.sort_values("mean"), dim, [("Promedio", "mean", PRIMARY, MUTED)], False,
                marcador=("Mediana", "median", ACCENT), key=f"ch_ingreso_{dim}", completo=completo)


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
                cols = [st.container()] if len(fila) == 1 else st.columns(len(fila), gap="large")
                for col, (dim, tit, opts) in zip(cols, fila):
                    with col:
                        fn(df, dim, tit, completo=len(fila) == 1, **opts)


# ---------------------------------------------------------------------------
# COMPONENTES DE INTERFAZ
# ---------------------------------------------------------------------------
def kpi(valor, etiqueta, clase):
    st.markdown(f'<div class="kpi-v {clase}">{valor}</div><div class="kpi-l">{etiqueta}</div>',
                unsafe_allow_html=True)


def ir(pagina):
    st.session_state.page = pagina


NAV = [("formalidad", "Análisis descriptivo formalidad"), ("ingresos", "Análisis descriptivo ingresos"),
       ("salario", "Modelo predictivo ingresos"), ("empleo", "Modelo predictivo formalidad")]


def barra_nav():
    with st.container(key="nav"):
        with st.container(key="nav_brand"):
            icono, marca = st.columns([1, 6], vertical_alignment="center")
            with icono:
                st.button("Inicio", key="nav_inicio", icon=":material/home:", help="Ir a la portada",
                          on_click=ir, args=("inicio",))
            marca.markdown('<div class="brand">Mercado laboral</div>', unsafe_allow_html=True)
        with st.container(key="nav_items"):
            for col, (k, etiqueta) in zip(st.columns(len(NAV), vertical_alignment="center"), NAV):
                col.button(etiqueta, key=f"nav_{k}", on_click=ir, args=(k,),
                           type="primary" if st.session_state.page == k else "secondary")
    st.markdown('<hr class="rule">', unsafe_allow_html=True)


FILTROS = [("anio", "Año"), ("Mes Letras", "Mes"), ("departamento", "Departamento"),
           ("sexo", "Sexo"), ("nivel_educativo", "Educación")]


def barra_filtros(df_raw, clave):
    """Filtros horizontales y compactos; vacío = Todos. Devuelve el DataFrame filtrado."""
    sel = {}
    with st.container(key="filters"):
        cols = st.columns([1, 1, 1.2, 1, 1.2, 1.1], gap="small", vertical_alignment="center")
        for col, (c, etiqueta) in zip(cols, FILTROS):
            opciones = MESES_ORDEN if c == "Mes Letras" else sorted(df_raw[c].dropna().unique().tolist(), key=str)
            sel[c] = col.multiselect(etiqueta, opciones, placeholder=f"{etiqueta}: todos",
                                     key=f"f_{clave}_{c}", label_visibility="collapsed")
        df = df_raw
        for c, valores in sel.items():
            if valores:
                df = df[df[c].isin(valores)]
        cols[-1].markdown(f'<div class="aux">{fmt_n(len(df))} de {fmt_n(len(df_raw))} registros</div>',
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
    """Portada: pantalla separada, sin navegación ni asistente. El mapa es el fondo (ver CSS)."""
    st.markdown(
        '<div class="cover-content">'
        '<div class="cover-title">Mercado laboral<br>en Colombia</div>'
        '<div class="cover-sub">Una solución para tomar decisiones sobre el empleo</div>'
        '</div>', unsafe_allow_html=True)
    with st.container(key="cover_cta"):
        st.button("Iniciar", key="cover_go", on_click=ir, args=("formalidad",))
    st.markdown('<div class="cover-foot">Fuente: Gran Encuesta Integrada de Hogares (GEIH), DANE.</div>',
                unsafe_allow_html=True)


def pagina_formalidad(df_raw):
    cabecera = st.container()
    df = barra_filtros(df_raw, "formalidad")
    pf, pnf = pct_formal_no_formal(df)
    with cabecera, st.container(key="kpis"):
        c0, c1, c2 = st.columns([2.2, 1, 1], gap="medium", vertical_alignment="center")
        with c0: encabezado("Análisis descriptivo formalidad", "Proporción de personas ocupadas con empleo formal y no formal.")
        with c1: kpi(fmt_pct(pf), "Trabajo formal", "k-primary")
        with c2: kpi(fmt_pct(pnf), "Trabajo no formal", "k-teal")
    bloque_graficos(df, grafico_formalidad)
    pie()


def pagina_ingresos(df_raw):
    cabecera = st.container()
    df = barra_filtros(df_raw, "ingresos")
    prom, med = promedio_mediana_ingreso(df)
    with cabecera, st.container(key="kpis"):
        c0, c1, c2 = st.columns([2.2, 1, 1], gap="medium", vertical_alignment="center")
        with c0: encabezado("Análisis descriptivo ingresos", "Promedio y mediana del ingreso laboral total.")
        with c1: kpi(fmt_cop(prom), "Ingreso promedio", "k-primary")
        with c2: kpi(fmt_cop(med), "Mediana", "k-accent")
    bloque_graficos(df, grafico_ingreso)
    pie()


# Segmentadores pendientes: (nombre, tipo de información). Reemplazar por las variables definitivas del modelo.
SEGMENTADORES_PENDIENTES = [
    ("Perfil demográfico", "sexo, edad, estado civil"),
    ("Educación", "nivel educativo"),
    ("Ubicación", "departamento"),
    ("Ocupación", "sector económico, oficio"),
    ("Tipo de empleo", "posición ocupacional, contrato"),
]


def paso(n, titulo, texto, etiqueta=""):
    tag = f'<span class="tag">{etiqueta}</span>' if etiqueta else ""
    st.markdown(f'<div class="step"><span class="step-n">{n}</span><span class="step-t">{titulo}</span>{tag}</div>'
                f'<div class="step-sub">{texto}</div>', unsafe_allow_html=True)


def predecir(clave):
    """Punto de integración del modelo: ejecutar la predicción con las variables seleccionadas."""
    st.session_state[f"predijo_{clave}"] = True


def pagina_modelo(clave, titulo, subtitulo, resultado):
    encabezado(titulo, subtitulo)
    st.markdown('<div style="height:1rem"></div>', unsafe_allow_html=True)
    izq, der = st.columns([1, 1.7], gap="large")
    with izq, st.container(key=f"panel_vars_{clave}"):
        paso(1, "Selecciona las variables",
             "Describe el perfil que quieres analizar. Cada selector se completará con una variable "
             "cuando el modelo esté definido.", "Por definir")
        for i, (nombre, ejemplo) in enumerate(SEGMENTADORES_PENDIENTES):
            st.selectbox(nombre, [], index=None, placeholder=f"Seleccionar: {ejemplo}",
                         disabled=True, key=f"{clave}_var_{i}")
        st.markdown('<hr class="rule">', unsafe_allow_html=True)
        paso(2, "Ejecuta la predicción", "Cuando hayas elegido las variables, pulsa Predecir.")
        with st.container(key=f"predecir_{clave}"):
            st.button("Predecir", key=f"btn_predecir_{clave}", on_click=predecir, args=(clave,))
    with der, st.container(key=f"panel_result_{clave}"):
        paso(3, "Revisa los resultados", f"Aquí se mostrará {resultado}.")
        if st.session_state.get(f"predijo_{clave}"):
            st.caption("El modelo aún no está conectado, por lo que no se generó ninguna predicción.")
        st.markdown('<div class="result-empty">Sin resultados todavía</div>', unsafe_allow_html=True)
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
    pagina_modelo("salario", "Modelo predictivo ingresos",
                  "Estimación del ingreso laboral según el perfil de la persona.", "la proyección de salario")
else:
    pagina_modelo("empleo", "Modelo predictivo formalidad",
                  "Estimación de la probabilidad de conseguir un empleo formal.", "la probabilidad de empleo formal")

if pagina != "inicio":
    asistente()

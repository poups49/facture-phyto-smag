
import streamlit as st
import pandas as pd
import pytesseract
from PIL import Image
import io, re
from pdf2image import convert_from_bytes

st.set_page_config(page_title="Démo Facture Phyto → SMAG", layout="wide")
st.title("🔧 Démo : Facture Terrena/CAPL → Registre SMAG")

uploaded = st.file_uploader("📄 Choisis ta facture (PNG, JPG, JPEG, PDF)", type=["png","jpg","jpeg","pdf"])
if uploaded:
    # Conversion PDF en image
    if uploaded.type == "application/pdf":
        images = convert_from_bytes(uploaded.read(), dpi=300)
        img = images[0]
    else:
        img = Image.open(uploaded)

    st.image(img, caption="Document chargé", use_column_width=True)
    text = pytesseract.image_to_string(img, lang="fra")
    st.subheader("🔍 Texte extrait")
    st.text_area("", text, height=200)

    produits, date, fournisseur = [], "", ""
    for ligne in text.split("\n"):
        if not date:
            d = re.search(r"(\d{2}/\d{2}/\d{4})", ligne)
            date = d.group(1) if d else date
        if not fournisseur and ("Terrena" in ligne or "CAPL" in ligne):
            fournisseur = "Terrena" if "Terrena" in ligne else "CAPL"
        m = re.match(r".*(DECIS PROTECH|.*TRICHO).*?(\d+)[\s]*([LPCE]{1,3}).*?([0-9]+,[0-9]{2})", ligne)
        if m:
            nom, qty_s, unit, price_s = m.groups()
            produits.append({
                "Date": date,
                "Fournisseur": fournisseur,
                "Produit": nom.strip(),
                "Quantité": int(qty_s),
                "Unité": unit,
                "Prix unitaire HT (€)": float(price_s.replace(",", ".")),
                "Volume total": f"{qty_s} {unit}"
            })

    if produits:
        df = pd.DataFrame(produits)
        st.subheader("📋 Produits détectés")
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("⬇️ Télécharger CSV", data=csv, file_name="registre_phyto.csv", mime="text/csv")
    else:
        st.info("Aucun produit détecté — essaie avec une facture Terrena ou CAPL.")

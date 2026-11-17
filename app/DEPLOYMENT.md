# Deployment

The app entry point is app/streamlit_app.py. Dependencies are in the root requirements.txt. The PDF report and version 2 CSVs are part of the repository and the app requires no service credentials to calculate, chart or serve downloads.

## Local preview

From the repository root with Python 3.13:

~~~sh
python -m pip install -r requirements.txt
python -m streamlit run app/streamlit_app.py --server.address 127.0.0.1
~~~

## Publication and Community Cloud

1. After the owner approves publication, confirm the licence choice and copyright notice. Push the reviewed main branch to the authorised GitHub repository named transformer-loss-optimisation.
2. Set the repository link in the public deployment configuration after verifying its address. The optional PORTFOLIO_GITHUB_URL environment variable works for local self-hosting. On Community Cloud, set PORTFOLIO_GITHUB_URL in the app secrets if using the configuration route, or set the verified link in the app and commit it.
3. With repository admin access, deploy from Streamlit Community Cloud using branch main, entry point app/streamlit_app.py and Python 3.13. An initial Streamlit-to-GitHub authorisation may be required.
4. Verify the public GitHub repository, the README and the report/figure links. Verify the externally hosted page, both sliders, reset, the scenario selector and the CSV/PDF downloads. Check 9.567 W at the medium baseline and 9.342 W at 475 turns and 15.0 cm². Add the verified hosted address to the README.

[Streamlit Community Cloud deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)

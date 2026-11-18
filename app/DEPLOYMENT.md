# Deployment

The app entry point is app/streamlit_app.py. Dependencies are in the root requirements.txt. The PDF report and model CSVs are part of the repository and the app requires no service credentials to calculate, chart or serve downloads.

## Local preview

From the repository root with Python 3.13:

~~~sh
python -m pip install -r requirements.txt
python -m streamlit run app/streamlit_app.py --server.address 127.0.0.1
~~~

## Publication and Community Cloud

1. After approval to deploy publicly, connect the GitHub repository to Streamlit Community Cloud.
2. Choose branch main, entry point app/streamlit_app.py and Python 3.13. The app uses its public GitHub address by default. PORTFOLIO_GITHUB_URL can point the app to a fork.
3. Verify both sliders, reset, the scenario selector and the CSV/PDF downloads. Check 9.567 W at the medium baseline and 9.342 W at 475 turns and 15.0 cm².
4. Add the verified hosted address to the [README](../README.md).

[Streamlit Community Cloud deployment](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy)

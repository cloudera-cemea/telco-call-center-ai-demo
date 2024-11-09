# Telco Call Center AI Demo on Cloudera Machine Learning.

## Description
The Telco Call Center AI Demo is a demonstration project designed to showcase the capabilities of Cloudera Machine Learning (CML) in a fictional telecommunications call center environment. It integrates AI models to enhance customer service by retrieving customer information and assessing churn risk. The project is set up using Cloudera Accelerated Machine Learning Projects (AMPs) and involves deploying a prototype, configuring environment variables, and accessing a web application. The application includes endpoints for sentiment analysis and LLM integration, and it uses a Flask-based frontend for user interaction. The project is configured through a .project-metadata.yaml file, which specifies deployment details and resource allocations.

## Installation
To set up the Telco Call Center AI Demo using Cloudera Accelerated Machine Learning Projects (AMPs), follow these steps:

1. **Deploy the AMP:**
   - Navigate to your Cloudera Machine Learning workspace and visit "Deploy a Prototype".
   - Search for and select the "Telco Call Center AI Demo" AMP.
   - If you can't find it, deploy it from the GitHub URL: https://github.com/cloudera-cemea/telco-call-center-ai-demo
   - Follow the on-screen instructions to deploy the project. This will automatically configure the environment and set up the necessary resources as specified in the `project-metadata.yaml`.

2. **Configure Environment Variables:**
   - You will be prompted to provide the following environment variables when starting the deployment:
     - `SPARK_DATA_LAKE_CONNECTION`: Name of Spark Data Lake connection for loading demo data. If you are not sure, contact the administrator of the workspace. Required.
     - `WORKLOAD_PASSWORD`: Password for the Cloudera user deploying the project. Required.
     - `OPENAI_API_KEY`: API key for OpenAI model access. Required.
     - `DEMO_DATABASE_NAME`: Name of the database for demo data (default: `telco_call_center_ai`). Optional.
     - `DEMO_TABLE_NAME`: Name of the table for demo data (default: `customer_info`). Optional.

3. **Wait for the AMP deployment process to finish:**
   - The deployment process will take a few minutes to complete. You can monitor the progress in the Cloudera Machine Learning workspace. The following assets will be deployed during the process:
     - Setup of demo data.
     - Model endpoint for sentiment analysis.
     - Model endpoint for LLM integration and customer information retrieval.
     - Frontend aplication for user interaction with web speech API and model endpoints.

4. **Access the application in your web browser:**
    - Once the deployment is complete, you can access the application by navigating to the URL provided in the Cloudera Machine Learning workspace. The frontend application will be accessible under Applications.
    - Use the interface to input customer details and retrieve information using the AI model.

# Features
- Integration with Spark Data Lake for data management.
- LLM model integration for customer information retrieval.
- Flask web application for user interaction.

# Contributing
We welcome contributions! Please fork the repository and open a pull request.

# License
This project is licensed under the MIT License. See the LICENSE file for details.

# Contact Information
For questions or support, please contact the maintainer at mengelhardt@cloudera.com.

# Acknowledgments
Special thanks to Cloudera for providing the tools and platform to develop this demo.

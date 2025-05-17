FROM continuumio/miniconda3

# Set working directory
WORKDIR /app

# Copy all project files into the container
COPY . .

# Create the environment and install dependencies
RUN conda create -n ai_scientist python=3.11 -y \
    && echo "conda activate ai_scientist" >> ~/.bashrc

# Activate env and install packages
RUN /bin/bash -c "source ~/.bashrc && conda activate ai_scientist && \
    conda install -y pytorch torchvision torchaudio cpuonly -c pytorch && \
    conda install -y anaconda::poppler && \
    conda install -y -c conda-forge chktex && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install anthropic[bedrock]"

# Expose FastAPI port
EXPOSE 8000

# Command to run app on container start
CMD ["/bin/bash", "-c", "source ~/.bashrc && conda activate ai_scientist && python -m uvicorn server:app --host 0.0.0.0 --port 8000"]

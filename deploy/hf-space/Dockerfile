# Hugging Face Docker Space of the CoBaIR web GUI.
# Uses the same launch path as `cobair-web` locally: pre-built frontend + backend on one port.
FROM python:3.12-slim

# Hugging Face runs Docker Spaces as user 1000
RUN useradd --create-home --uid 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH \
    PYTHONUNBUFFERED=1
WORKDIR /home/user/app

# the wheel built by the release workflow (contains the frontend)
COPY --chown=user dist/*.whl ./
RUN pip install --no-cache-dir --user "$(ls ./*.whl)[web]" && rm ./*.whl

EXPOSE 7860
# one worker, no storage: configs are up- and downloaded, drafts live in the browser
CMD ["cobair-web", "--host", "0.0.0.0", "--port", "7860", "--no-browser"]

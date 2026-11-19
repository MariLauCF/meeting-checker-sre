# Meeting Checker

Meeting Checker is an application for the SRE Academy Final Project.

This app checks the meetings included in it to identify if they are ready or need further action.

A meeting is READY when:

- It has a room.
- There are no pending RSVPs.
- Nobody declined the meeting.

If one of these conditions is not completed, the meeting is not ready.

App developed in the Ubuntu terminal with help from Copilot.

The project includes the tools studied in the academy:

- Python
- Flask
- Docker
- Kubernetes
- Minikube
- Prometheus
- Grafana
- Alertmanager
- Helm
- GitHub

## Deployment of the application

Meeting Checker gets the information from the `meetings.json` file, and it contains 4 meetings:

- 2 ready meetings
- 2 not ready meetings
- 1 missing room
- 1 pending RSVP
- 0 declined RSVPs

### Meeting Checker Application

screenshots/01-application.png

## Docker

To build the Docker image:

```bash
docker build -t meeting-checker:v1 .
```

To run it:

```bash
docker run -d --name meeting-checker -p 5000:5000 meeting-checker:v1
```

The application can be opened in the browser at:

```text
http://localhost:5000
```

### Docker Image

screenshots/02-docker.png

## Kubernetes

To start Minikube:

```bash
minikube start --driver=docker
```

To create the namespace:

```bash
kubectl create namespace meeting-checker
```

To build the image for Meeting Checker:

```bash
minikube image build -t meeting-checker:v1 .
```

To deploy Meeting Checker:

```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

To check the Pod:

```bash
kubectl get pods -n meeting-checker
```

### Kubernetes

screenshots/03-kubernetes.png

## Prometheus, Grafana and Alertmanager

The monitoring tools are installed with Helm.

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

To create the monitoring namespace:

```bash
kubectl create namespace monitoring
```

To install the monitoring stack:

```bash
helm install monitoring prometheus-community/kube-prometheus-stack \
  --namespace monitoring
```

The monitoring stack includes:

- Prometheus
- Grafana
- Alertmanager

### Monitoring

screenshots/08-monitoring.png

## Prometheus

The ServiceMonitor can be deployed with:

```bash
kubectl apply -f kubernetes/servicemonitor.yaml
```

For example, this query:

```text
meeting_checker_total_meetings
```

shows the total number of meetings.

### Prometheus

screenshots/04-prometheus.png

## Grafana

The dashboard shows:

- Total Meetings
- Ready Meetings
- Not Ready Meetings
- Meeting Readiness
- Missing Rooms
- Pending RSVPs
- Declined RSVPs

The dashboard file is saved in:

```text
monitoring/grafana-dashboard.json
```

### Grafana Dashboard

screenshots/05-grafana.png

## Alerts

Prometheus has three alert rules:

- MeetingMissingRoom
- PendingMeetingRSVP
- MeetingCheckerDown

The rules are located in:

```text
monitoring/prometheus-rules.yaml
```

They can be deployed with:

```bash
kubectl apply -f monitoring/prometheus-rules.yaml
```

### Prometheus Alerts

screenshots/06-alerts.png

## Alertmanager

Alertmanager receives the alerts created by Prometheus.

For the test, the sample data has one meeting without a room and one pending RSVP. This makes it possible to see the alerts working.

### Alertmanager

screenshots/07-alertmanager.png

---

Maria Laura Cascante Fallas

SRE Academy Final Project

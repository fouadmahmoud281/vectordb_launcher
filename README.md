# VectorDB Interface Deployment Guide

## Overview

This repository contains Ansible automation for deploying the VectorDB Interface, a Streamlit-based web application that provides a user interface for vector database operations including embedding creation, document indexing, and semantic search.


## Repository Structure

```
vectordb-deployment/
├── ansible.cfg                # Ansible configuration
├── inventory.ini              # Server inventory
├── playbook.yml               # Main playbook
├── Vagrantfile                # Local testing configuration
├── README.md                  # This documentation
├── roles/
│   └── vectordb-app/          # Main application role
│       ├── defaults/          # Default variables
│       │   └── main.yml
│       ├── tasks/             # Deployment tasks
│       │   └── main.yml
│       ├── templates/         # Jinja2 templates
│       │   ├── app_config.j2  # App configuration template
│       │   └── service.j2     # Systemd service template
│       └── vars/
│           └── main.yml       # Role-specific variables
├── vars/
│   ├── environment.yml        # Environment-specific variables
│   ├── production.yml         # Production environment
│   └── staging.yml            # Staging environment
└── files/
    └── app/                   # Application source code
        ├── app.py             # Main Streamlit application
        ├── embed.py           # Embedding functionality
        ├── index.py           # Document indexing functionality
        ├── search.py          # Search functionality
        ├── utils.py           # Utility functions
        └── requirements.txt   # Python dependencies
```

## Prerequisites

- Ansible 2.9+
- Target servers with:
  - Ubuntu 20.04 LTS or newer
  - Python 3.8+ installed
  - Sudo access

For local testing:
- Vagrant 2.2+
- VirtualBox 6.1+

## Key Variables

The application is highly configurable through variables. The most important ones are:

| Variable | Description | Default |
|----------|-------------|---------|
| `app_title` | Application title displayed in header | "VectorDB Interface" |
| `app_subtitle` | Application subtitle | "Powerful vector database operations for AI applications" |
| `api_base_url` | Base URL for the backend API | "https://embeddings100.cloud-stacks.com" |
| `app_port` | Port for Streamlit to listen on | 8501 |
| `app_dir` | Directory where app is deployed | "/opt/vectordb-app" |
| `app_user` | System user to run the app | "streamlit" |

See `roles/vectordb-app/defaults/main.yml` for a complete list of variables and their defaults.

## Deployment Instructions

### Production Deployment

1. Clone this repository:
   ```bash
   git clone https://github.com/your-org/vectordb-deployment.git
   cd vectordb-deployment
   ```

2. Update the `inventory.ini` file with your target servers:
   ```ini
   [app_servers]
   app1.example.com ansible_user=ubuntu
   app2.example.com ansible_user=ubuntu
   
   [load_balancers]
   lb.example.com ansible_user=ubuntu
   ```

3. Configure environment-specific variables by creating/editing files in the `vars/` directory.

4. Run the playbook:
   ```bash
   ansible-playbook playbook.yml -i inventory.ini
   ```

5. For a specific environment:
   ```bash
   ansible-playbook playbook.yml -i inventory.ini -e "@vars/production.yml"
   ```

### Local Testing with Vagrant

1. Start the Vagrant VM:
   ```bash
   vagrant up
   ```

2. Access the application at http://localhost:8501

3. To re-run provisioning after changes:
   ```bash
   vagrant provision
   ```

4. To destroy the test environment:
   ```bash
   vagrant destroy
   ```

## Configuration Details

### Application Configuration

The application configuration is templated using `app_config.j2`, which generates a Python file with all necessary configuration. This approach allows:

1. Centralized configuration management via Ansible
2. Environment-specific configurations
3. Runtime variable access in the application

Key configurations:
- API endpoints
- Theme colors
- Application metadata
- System status indicators

### Service Configuration

The app runs as a systemd service, configured via the `service.j2` template. This provides:
- Automatic start on boot
- Restart on failure
- System logging integration
- Proper process management

### Custom Variables by Environment

Create environment-specific files in the `vars/` directory:

```yaml
# vars/production.yml
app_title: "Production VectorDB"
api_base_url: "https://api.production.example.com"
enable_monitoring: true
```

```yaml
# vars/staging.yml
app_title: "Staging VectorDB"
api_base_url: "https://api.staging.example.com"
enable_monitoring: false
```

## Customization & Optimization

### Adding New Variables

1. Add default values in `roles/vectordb-app/defaults/main.yml`
2. Update the template in `roles/vectordb-app/templates/app_config.j2`
3. Reference the new variables in environment-specific files

### System Requirements Tuning

Default allocations are set for typical workloads. For higher traffic:

1. Update system packages in `roles/vectordb-app/tasks/main.yml`
2. Add memory/CPU requirements in your Vagrantfile for testing
3. Configure resource limits in the systemd service template

```yaml
# Example memory optimization in systemd service template
[Service]
...
MemoryLimit=2G
CPUQuota=150%
```

### Performance Optimizations

1. **Caching**: Add Redis for session state persistence:
   ```yaml
   # Add to tasks/main.yml
   - name: Install Redis
     apt:
       name: redis-server
       state: present
     become: true
   ```

2. **Load Balancing**: Set up Nginx as a reverse proxy for multiple instances:
   ```yaml
   # Add to playbook.yml
   - hosts: load_balancers
     roles:
       - role: nginx-loadbalancer
   ```

3. **Static Files**: Serve static assets from Nginx instead of Streamlit:
   ```nginx
   # Example Nginx optimization
   location /static {
     alias /opt/vectordb-app/static;
     expires 7d;
   }
   ```

## Monitoring & Maintenance

### Log Access

```bash
# View application logs
sudo journalctl -u vectordb-app.service

# Follow logs in real-time
sudo journalctl -u vectordb-app.service -f
```

### Restarting the Service

```bash
# Restart the application
sudo systemctl restart vectordb-app

# Check status
sudo systemctl status vectordb-app
```

### Updating the Application

1. Update code in `files/app/`
2. Run the playbook with the `--tags update` option:
   ```bash
   ansible-playbook playbook.yml --tags update
   ```

## Extending the Deployment

### Adding SSL/TLS Support

1. Add a role for Let's Encrypt certificate generation
2. Configure Nginx to terminate SSL
3. Update playbook to include certificate rotation

### Database Integration

For persistent storage:
1. Add a database role (PostgreSQL/MongoDB)
2. Configure connection variables
3. Update app configuration template

### CI/CD Integration

Example GitLab CI configuration:

```yaml
# .gitlab-ci.yml
stages:
  - test
  - deploy

test_ansible:
  stage: test
  script:
    - ansible-lint playbook.yml
    - vagrant up
    - # Add tests against the Vagrant VM
    - vagrant destroy -f

deploy_staging:
  stage: deploy
  script:
    - ansible-playbook playbook.yml -i inventory.ini -e "@vars/staging.yml"
  only:
    - develop

deploy_production:
  stage: deploy
  script:
    - ansible-playbook playbook.yml -i inventory.ini -e "@vars/production.yml"
  only:
    - main
  when: manual
```

## Security Considerations

- The playbook creates a dedicated system user for running the application
- Systemd service configuration includes security hardening
- Application runs with minimal required permissions

Additional security measures to consider:
- Enable firewall rules
- Implement API authentication
- Configure HTTPS
- Set up network segmentation

## Troubleshooting

### Common Issues

1. **Service Fails to Start**
   - Check logs: `sudo journalctl -u vectordb-app.service -n 50`
   - Verify dependencies are installed: `pip list`
   - Check file permissions: `ls -la /opt/vectordb-app/`

2. **API Connection Failures**
   - Verify network connectivity: `curl -v <api_base_url>/health`
   - Check API configuration in `app_config.py`
   - Look for firewall restrictions

3. **Ansible Deployment Errors**
   - Run with increased verbosity: `ansible-playbook playbook.yml -vvv`
   - Check for syntax errors: `ansible-playbook playbook.yml --syntax-check`
   - Verify inventory connectivity: `ansible all -m ping`

## Role Tags

The playbook uses tags for selective execution:

- `install`: Initial installation tasks
- `config`: Configuration tasks only
- `service`: Service management tasks
- `update`: Application code update
- `dependencies`: Python dependencies installation
- `system`: System-level configurations

Example: Update application code only
```bash
ansible-playbook playbook.yml --tags update
```

## Best Practices for Modifications

1. **Version Control**: Commit all changes to the Ansible configurations
2. **Testing**: Test changes in Vagrant before pushing to production
3. **Idempotency**: Ensure tasks are idempotent (can run multiple times safely)
4. **Documentation**: Update this README when adding new features
5. **Secrets**: Use Ansible Vault for sensitive information:
   ```bash
   ansible-vault create secrets.yml
   ansible-playbook playbook.yml --ask-vault-pass
   ```

## Contributors

- DevOps Team @ obelion

## License

IMT licence
---

For any questions or issues, please contact the DevOps team at obelion@gmail.com.

# Arkane Zone — Initial repository audit

**Audit date:** 2 November 2026  
**Repository:** https://github.com/Cristianco9/arcakane-zone  
**Default branch inspected:** `main`

## 1. Repository snapshot

- Public GitHub repository, default branch `main`.
- One branch was visible during the audit: `main`.
- No pull requests were found during the audit.
- The root contains a README, Django project configuration, six Django applications, templates, migrations, seed data and a small pytest suite.
- No Dockerfile, Docker Compose file or GitHub Actions workflow was found in the inspected tree.

## 2. Business context inferred from implementation

Arkane Zone is a web-based video game store. The implemented domain includes a video game catalog, customer accounts, shopping cart, orders, simulated payments, sales/inventory reports and customer support.

The seed command contains sample games for PC, PlayStation 5, Xbox Series X and Nintendo Switch, with categories, genres, price and stock data.

This is a code-based reconstruction, not a validated statement from the original business owner. The team should confirm the intended business rules, target users, geographic scope, delivery/fulfillment model and whether the catalog represents physical or digital products.

## 3. Technology stack observed

- Python 3.12 and Django 5.2.
- PostgreSQL using `psycopg2-binary` and `DATABASE_URL`.
- Django Templates, Tailwind CSS CDN and HTMX 2.0.4.
- django-unfold for the admin interface.
- Gunicorn and WhiteNoise.
- Optional S3-compatible media storage through boto3 / django-storages.
- Pytest configuration and tests.
- Render deployment manifests (`render.yaml`, `build.sh`).

## 4. Application inventory

| App | Observed responsibilities |
|---|---|
| `cuentas` | Custom user, role, registration, profile and password update |
| `catalogo` | Categories, platforms, genres, video games, list/filter/detail |
| `pedidos` | Pending cart, order details, quantity changes, order history and cancellation |
| `pagos` | Simulated payment, payment record and sale registration |
| `reportes` | Dashboard, sales, inventory and video game reports |
| `soporte` | Contact form, information request and help page |

## 5. Verified strengths

- Apps have a recognizable separation by business domain.
- Data models and initial migrations exist for the primary entities.
- The project has a custom user model and role model.
- Cart and payment logic are partly separated into service functions.
- Database transactions and row locks are used in parts of the order/payment flow.
- A seed management command exists.
- A Render build/start configuration exists.
- Tests exist for cart rules, payment results, order cancellation and report authorization.

## 6. Initial risks and questions to validate

### R1 — Payment retry conflicts with one-payment-per-order model
The help page says a rejected payment can be retried. However, `Pago.pedido` is a OneToOne relation, and `procesar_pago_simulado` creates a new `Pago` record for every attempt. A second attempt for the same order may violate the database uniqueness constraint. Reproduce with a test before changing the model.

### R2 — Test dependencies are not declared in requirements
The repository has pytest configuration and imports pytest in the suite, but `requirements.txt` does not list pytest or pytest-django. Confirm the intended development dependency management and provide a reproducible test setup.

### R3 — Tests are incomplete
The dedicated `tests/` directory includes authorization, cancellation, cart and payment tests. Several app-level `tests.py` files are placeholders. Coverage for registration, profile changes, catalog filtering, support submission, report filtering and other paths needs investigation.

### R4 — Role model and staff authorization may diverge
A custom `Rol` with an administrator value exists, but report views use `staff_member_required`, templates use `user.is_staff`, and the `es_administrador` property is not used in the inspected paths. Confirm whether the intended source of authorization is Django staff/superuser status, the custom role, or both.

### R5 — Cart uniqueness under concurrent requests
`get_or_create_carrito` creates a pending order based on customer and state, but the inspected model does not define a unique database constraint for one pending cart per customer. Assess concurrency behavior and data integrity before proposing a change.

### R6 — Input validation and error handling
The cart update view casts a submitted quantity directly to `int`. Invalid input may raise an exception rather than produce a form-level validation message. Review malformed and boundary inputs across views and forms.

### R7 — Production email configuration
The current settings use Django's console email backend, with a comment indicating that SMTP should be configured for production. Confirm whether password reset is intended to work in the deployed environment.

### R8 — README needs maintenance
A README exists, but its clone URL points to a different owner/repository name. It also lacks validated business context, user roles, functional diagrams, test setup prerequisites and a clear statement distinguishing simulated payments from real payment processing.

### R9 — CI/CD and containerization not found
No workflow YAML, Dockerfile or Compose file appears in the inspected default-branch tree. Confirm whether these are intentionally out of scope or should be part of a later DevOps improvement.

## 7. Important constraints before implementation

- Payment processing is explicitly simulated in the current help page; there is no evidence of a real payment gateway.
- Do not assume the platform is a production-ready e-commerce system.
- Do not infer physical shipping, digital delivery, refunds, inventory sourcing or commercial policies unless validated.
- Keep a record of behavior before modifying it, so inherited features are not accidentally removed.
- Preserve secrets and production data; use a separate test database.

## 8. Next actions

Use the Sprint 1 plan in `docs/sprints/SPRINT-1.md` to validate this initial audit with the full team. Update this document as hypotheses become verified findings.

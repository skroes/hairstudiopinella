# Hosting Setup

## Netlify

- **Site ID:** friendly-payne-e31ce8
- **URL:** https://www.hairstudiopinella.nl
- **Netlify URL:** https://friendly-payne-e31ce8.netlify.app
- **Deploy:** Automatisch vanuit GitHub (push to deploy)
- **Login:** GitLab OAuth op app.netlify.com

## GitHub Repository

- **Repo:** https://github.com/skroes/hairstudiopinella
- **Branch:** master

## Deployment

Push naar `master` branch triggert automatisch een Netlify deploy.

```bash
git add -A
git commit -m "beschrijving"
git push
```

## Historie

- **2022-09-18:** Verhuisd van AWS S3 naar Netlify
- **Pre-2022:** Gehost op AWS S3 bucket `s3://www.hairstudiopinella.nl` (bucket bestaat niet meer)

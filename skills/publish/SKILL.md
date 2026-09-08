---
name: publish
description: Publish a local file to a durable public URL with native gcloud storage commands. Use when a generated image, screenshot, recording, PDF, APK, or other artifact needs a URL that outlives the session; first decide whether Cloud Storage or Google Drive is the correct destination.
---

# Publish

Use the installed `gcloud` CLI directly. Discover the current project and
bucket every time rather than relying on ambient defaults.

## Choose the destination

| Consumer | Destination |
| --- | --- |
| Anonymous renderer such as a Markdown image, Notion image block, or web page | A deliberately public Cloud Storage bucket |
| A person opening or downloading a private/shared file | Google Drive through the `google-drive` plugin |

Never put personal, client-confidential, or private material in a public bucket.
When the correct access posture is unclear, ask before uploading.

## Discover the exact project and bucket

Do not infer either from names and do not rely on ambient project configuration.

```bash
gcloud auth list --filter="status:ACTIVE" --format="value(account)"
gcloud projects list --format="table(projectId,name,projectNumber)"
gcloud storage ls --project=<project>
gcloud storage buckets describe gs://<bucket> \
  --project=<project> \
  --format="yaml(name,location,uniformBucketLevelAccess,publicAccessPrevention,softDeletePolicy,versioning)"
gcloud storage buckets get-iam-policy gs://<bucket> \
  --project=<project> \
  --format=json
```

Follow the bucket safety boundary and `<repo-or-owner>/<kind>/...` object layout
from the `storage` skill. Confirm that the chosen bucket is specifically for
published artifacts, is agent-writable, and grants the intended read role to
`allUsers`. If no account is active, use `gcloud auth login`; ADC is not needed
for native `gcloud` commands.

## Upload with gcloud

Choose the complete object name before writing. Use URL-safe path segments and
a collision-resistant filename. Protect new uploads with `--no-clobber`;
reusing an existing pathname is an overwrite and requires explicit approval.

```bash
gcloud storage cp ./output/sheet.png \
  gs://<public-bucket>/<repo-or-owner>/<kind>/<filename> \
  --no-clobber \
  --project=<project>
```

If `--no-clobber` reports that the destination already exists, choose a new
pathname; do not mistake the pre-existing object for a successful upload.

If the user explicitly approves replacing an existing object at a stable URL,
repeat the command without `--no-clobber` and name the exact destination first.

Verify the exact object after upload:

```bash
gcloud storage objects describe \
  gs://<public-bucket>/<repo-or-owner>/<kind>/<filename> \
  --project=<project> \
  --format="yaml(name,bucket,size,contentType,etag,updateTime)"
```

For a deliberately public object whose path segments are URL-safe, its stable
URL is:

```text
https://storage.googleapis.com/<public-bucket>/<URL-encoded-object-name>
```

Fetch the URL without Google credentials to verify anonymous access and the
expected content type before reporting it:

```bash
curl --fail --silent --show-error --location \
  --output /dev/null \
  --write-out '%{http_code} %{content_type}\n' \
  'https://storage.googleapis.com/<public-bucket>/<object-name>'
```

If anonymous access fails, report the mismatch; do not widen bucket or object
IAM unless the user explicitly approves that exact access change.

## Inspect and remove

```bash
gcloud storage ls gs://<bucket>/<prefix>/** --project=<project>
gcloud storage objects describe gs://<bucket>/<object> --project=<project>
```

Deleting may be unrecoverable. Only delete an exact object on explicit request,
after checking versioning and soft-delete as described by the `storage` skill.

After publishing, report the project, bucket, object name, and verified URL.

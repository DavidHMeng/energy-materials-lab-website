$ErrorActionPreference = "Stop"

if (Get-Command bundle -ErrorAction SilentlyContinue) {
  bundle install
  bundle exec jekyll serve --livereload
  exit $LASTEXITCODE
}

if (Get-Command docker -ErrorAction SilentlyContinue) {
  docker run --rm -it -p 4000:4000 -v "${PWD}:/site" -w /site ruby:3.3 `
    bash -lc "bundle install && bundle exec jekyll serve --host 0.0.0.0 --livereload"
  exit $LASTEXITCODE
}

Write-Error "Local preview requires Ruby + Bundler or Docker Desktop. See BUILD_SPEC.md."

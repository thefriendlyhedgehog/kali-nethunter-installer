#!/usr/bin/env sh

GIT_ACCOUNT=kalilinux
GIT_REPOSITORY=nethunter/build-scripts/kali-nethunter-kernels

ABORT() {
  [ "$1" ] && echo "Error: $*" >&2
  exit 1
}

cd "$(dirname "$0")" || ABORT "Failed to enter script directory!"

if [ -d kernels ]; then
  echo "The kernels directory already exists, choose an option:"
  echo "   U) Update kernels to latest commit (default)"
  echo "   D) Delete kernels folder and start over"
  echo "   C) Cancel"
  printf "[?] Your choice? (U/d/c): "
  read -r choice
  case ${choice} in
    U*|u*|"")
      echo "[i] Updating kernels (fetch & rebase)"
      cd kernels || ABORT "Failed to enter kernels directory!"
      git fetch && git rebase || ABORT "Failed to update kernels!"
      exit 0
      ;;
    D*|d)
      echo "[i] Deleting kernels folder"
      rm -rf kernels ;;
    *)
      ABORT ;;
  esac
fi

clonecmd="git clone"

printf "[?] Would you like to grab the full history of kernels? (y/N): "
read -r choice
case ${choice} in
  y*|Y*) ;;
  *)
    clonecmd="${clonecmd} --depth 1" ;;
esac

printf "[?] Would you like to use SSH authentication (faster, but requires a GitLab account with SSH keys)? (y/N): "
read -r choice
case $choice in
  y*|Y*)
    cloneurl="git@gitlab.com:${GIT_ACCOUNT}/${GIT_REPOSITORY}" ;;
  *)
    cloneurl="https://gitlab.com/${GIT_ACCOUNT}/${GIT_REPOSITORY}.git" ;;
esac

clonecmd="${clonecmd} $cloneurl kernels"
echo "[i] Running command: ${clonecmd}"

${clonecmd} || ABORT "Failed to git clone kernels!"

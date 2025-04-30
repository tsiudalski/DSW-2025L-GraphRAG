# ~/.bashrc inside container
parse_git_branch() {
  git rev-parse --abbrev-ref HEAD 2>/dev/null | sed 's/.*/(\0)/'
}
export PS1="\[\033[01;34m\]\u@\h \[\033[01;32m\]\w \[\033[01;33m\]\$(parse_git_branch)\[\033[00m\] \$ "
cd /workspace

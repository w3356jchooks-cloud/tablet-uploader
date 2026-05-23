TERMUX_PKG_HOMEPAGE=https://github.com/termux/termux-packages
TERMUX_PKG_DESCRIPTION="Privileged Android file manager and deployment hub"
TERMUX_PKG_LICENSE="GPL-3.0"
TERMUX_PKG_MAINTAINER="Developer <support@termux.dev>"
TERMUX_PKG_VERSION=1.0.0
TERMUX_PKG_SRCURL=https://github.com/termux/termux-packages
TERMUX_PKG_PLATFORM_INDEPENDENT=true

termux_step_make_install() {
    # This tells Termux where to place your files when a user installs it
    mkdir -p $TERMUX_PREFIX/bin
    mkdir -p $TERMUX_PREFIX/share/tablet-uploader
    
    # Copying your script files into the package
    cp $TERMUX_PKG_SRCDIR/tablet-uploader $TERMUX_PREFIX/bin/
    cp $TERMUX_PKG_SRCDIR/main.py $TERMUX_PREFIX/share/tablet-uploader/
    cp $TERMUX_PKG_SRCDIR/watcher.sh $TERMUX_PREFIX/share/tablet-uploader/
    
    chmod +x $TERMUX_PREFIX/bin/tablet-uploader
    chmod +x $TERMUX_PREFIX/share/tablet-uploader/watcher.sh
}

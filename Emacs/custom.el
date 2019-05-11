;; ~/.emacs.d/custom.el

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(Info-additional-directory-list
   (quote
    ("/usr/share/info/scrapy/" "/usr/share/info/python3.4/" "/usr/share/info/postgres/")))
 '(bmkp-desktop-jump-save-before-flag t)
 '(bmkp-last-as-first-bookmark-file "/home/alioth/.emacs.d/bookmarks")
 '(desktop-save-mode nil)
 '(org-agenda-files nil)
 '(org-confirm-babel-evaluate nil)
 '(org-icalendar-include-todo (quote unblocked))
 '(org-icalendar-use-deadline (quote (todo-due)))
 '(org-icalendar-use-scheduled (quote (todo-start)))
 '(org-modules
   (quote
    (org-bbdb org-bibtex org-docview org-gnus org-info org-irc org-mhe org-rmail org-w3m org-drill)))
 '(org-src-window-setup (quote other-frame))
 '(package-archives
   (quote
    (("melpa" . "https://melpa.org/packages/")
     ("gnu" . "http://elpa.gnu.org/packages/")
     ("org" . "http://orgmode.org/elpa/"))))
 '(package-selected-packages
   (quote
    (color-theme-modern simpleclip engine-mode htmlize langtool org elfeed elpy google-translate howdoi key-chord magit marshal org-bullets org-pomodoro pcache travis voca-builder ereader docker)))
 '(send-mail-function (quote smtpmail-send-it)))

(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )

(add-to-list 'custom-theme-load-path
	     (file-name-as-directory "/usr/local/share/emacs/site-lisp/replace-colorthemes"))

(load-theme 'dark-laptop t t)
(load-theme 'desert t t)
(load-theme 'euphoria t t)
(load-theme 'goldenrod t t)
(load-theme 'midnight t t)
(load-theme 'retro-green t t)
(load-theme 'taylor t t)
(enable-theme 'taylor)

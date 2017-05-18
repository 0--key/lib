;;(setq custom-file "~/.emacs.d/init-custom.el")
;;(load custom-file)
;;
(require 'package)
(add-to-list 'package-archives '("org"
. "http://orgmode.org/elpa/") t)
;; and MELPA
(add-to-list 'package-archives '("melpa"
             . "https://melpa.org/packages/"))
(package-initialize)

(tool-bar-mode -1)
(menu-bar-mode -1)
(scroll-bar-mode -1)
(setq sentence-end-double-space nil)

;; packages autoinstallation snippet
;; (setq packages-list '(docker ereader voca-builder travis pcache
;;     org org-pomodoro org-bullets marshal magit key-chord howdoi
;;     google-translate elpy elfeed color-theme bookmark+))
;; (unless package-archive-contents
;;   (package-refresh-contents))
;; (dolist (package packages-list)
;;   (unless (package-installed-p package)
;;     (package-install package)))

(custom-set-variables
 ;; custom-set-variables was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 '(package-selected-packages
   (quote
    (org bookmark+ color-theme elfeed elpy google-translate howdoi key-chord magit marshal org-bullets org-pomodoro pcache travis voca-builder ereader docker))))
(custom-set-faces
 ;; custom-set-faces was added by Custom.
 ;; If you edit it by hand, you could mess it up, so be careful.
 ;; Your init file should contain only one such instance.
 ;; If there is more than one, they won't work right.
 )

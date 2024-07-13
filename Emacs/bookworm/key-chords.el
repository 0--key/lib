;; KeyChords are below
;; General commants for vanilla ~Emacs~

(key-chord-define-global "uu" 'null)
(define-key key-translation-map (kbd "<key-chord> uu")  (kbd "C-x"))
(key-chord-define-global "yy" 'null)
(define-key key-translation-map (kbd "<key-chord> yy")  (kbd "M-x"))
(key-chord-define-global "hh" 'null)
(define-key key-translation-map (kbd "<key-chord> hh")  (kbd "C-h"))
(key-chord-define-global "vv" 'null)
(define-key key-translation-map (kbd "<key-chord> vv")  (kbd "C-c"))


;; Cursor Movement:
(key-chord-define-global "j;"     'move-end-of-line)
(key-chord-define-global "fa"     'move-beginning-of-line)
(key-chord-define-global "fd"     'left-word)

;; Scrolling
(key-chord-define-global "ij"     'scroll-down-command)
(key-chord-define-global "km"     'scroll-up-command)
(key-chord-define-global "IJ"     'scroll-other-window-down)
(key-chord-define-global "KM"     'scroll-other-window)


;; Frames and Windows management:
(key-chord-define-global "'#"     'other-frame)
(key-chord-define-global "]\\"     'other-frame)
(key-chord-define-global "#]"     'other-frame)
(key-chord-define-global "q1"     'delete-other-windows)
(key-chord-define-global "w2"     'split-window-below)
(key-chord-define-global "e3"     'split-window-right)
(key-chord-define-global "0o"     'delete-window)
(key-chord-define-global "oj"     'other-window)


;; Anti-clockwise -->
(key-chord-define-global "OJ"
			 (lambda ()
			   (interactive) (other-window -1)))
;; And frames in the stack as well -->
(key-chord-define-global "`1"
			 (lambda ()
			   (interactive) (other-frame -1)))

;; Registers
(key-chord-define-global "rw"     'window-configuration-to-register)
(key-chord-define-global "rj"     'jump-to-register)

;; Buffers
(key-chord-define-global "bn"     'list-buffers)
(key-chord-define-global "bv"     'switch-to-buffer)
(key-chord-define-global "fq"     'previous-buffer)
(key-chord-define-global "jp"     'next-buffer)
(key-chord-define-global "bk"     'kill-buffer)
(key-chord-define-global "b4"     'switch-to-buffer-other-window)
(key-chord-define-global "sq"
			 (lambda ()
			   (interactive) (save-some-buffers 1)))
(key-chord-define-global "ga"
			 (lambda ()
			   (interactive)
			   (switch-to-buffer "*Org Agenda*")))
(key-chord-define-global "un"
			 (lambda ()
			   (interactive)
			   (switch-to-buffer "*scratch*")))
(key-chord-define-global "i7"
			 (lambda ()
			   (interactive)
			   (switch-to-buffer "*info*")))
(key-chord-define-global "i8"
			 (lambda ()
			   (interactive)
			   (switch-to-buffer "*info*<2>")))
(key-chord-define-global "i9"
			 (lambda ()
			   (interactive)
			   (switch-to-buffer "*info*<3>")))
(key-chord-define-global "yn"
			 (lambda ()
			   (interactive)
			   (switch-to-buffer "*shell*")))
(key-chord-define-global "mn"
			 (lambda ()
			   (interactive)
			   (switch-to-buffer "*Messages*")))

;; Marks
(key-chord-define-global "m "     'set-mark-command)
;; Misc
(key-chord-define-global "fg"     'find-file)
(key-chord-define-global "ex"     'eval-region)
(key-chord-define-global "gs"     'magit-status)
(key-chord-define-global "vl"     'vc-print-log)
(key-chord-define-global "fm"     'follow-mode)
(key-chord-define with-editor-mode-map "dc"     'with-editor-finish) ;; ~cd~ in bash
(key-chord-define-global "pi"     'info-apropos)
;;
(key-chord-define-global "sf"     'swiper)
(key-chord-define-global "SF"     'swiper-backward)
;;
(key-chord-define-global "im"     'insert-register) ;; too common

;; Killing and Yanking
(key-chord-define-global "vf"     'kill-ring-save)
(key-chord-define-global "rf"     'kill-region)
(key-chord-define-global "rd"     'delete-region)
(key-chord-define-global "uy"     'yank)

;; Translation
(key-chord-define-global "tr"     'google-translate-at-point)
(key-chord-define-global "TR"     'google-translate-at-point-reverse)
(key-chord-define-global "tv"     'voca-builder/search-popup)
(key-chord-define-global "wt"     'dictionary-lookup-definition)
(key-chord-define-global "wd"     'mw-thesaurus-lookup-dwim)

;; Drilling
(key-chord-define org-mode-map "dr"     'org-drill-resume)
(key-chord-define org-mode-map "dt"     'org-drill-tree)

;; Bookmark + section
(key-chord-define-global "sb"     'bmkp-store-org-link)
(key-chord-define-global "bm"     'bmkp-bookmark-set-confirm-overwrite)
(key-chord-define-global "lb"     'bookmark-bmenu-list)
(key-chord-define-global "jb"     'bookmark-jump)
(key-chord-define-global "sb"     'bookmark-bmenu-save)

;; Org section
(global-set-key (kbd "C-c c") 'org-capture)
(key-chord-define org-mode-map "zv"     'vizier)
;;(key-chord-define org-mode-map "av"     'vizier-answer)

;; Clocked task capture for straight note as a point on the bullet
;; list:
;; - <captured text>;
;; - <captured text>;
(key-chord-define-global "cy"
			 (lambda ()
			   (interactive) (org-capture nil "cc")
			   (deactivate-mark)))
;; and for fleeting notes exactly:
(key-chord-define-global "cf"
			 (lambda ()
			   (interactive) (org-capture nil "nf")
			   (deactivate-mark)))
;;
(global-set-key (kbd "C-c a") 'org-agenda)
(key-chord-define org-mode-map "dc"     'org-capture-finalize)
(key-chord-define-global "qq"     'org-fill-paragraph)
;; (key-chord-define org-mode-map "km"     'org-meta-return) ;; useless
(key-chord-define org-mode-map "a["     'org-agenda-file-to-front)
(key-chord-define org-mode-map "a]"     'org-remove-file)
;; (key-chord-define org-mode-map "od"     'org-deadline) widely used 
;; (key-chord-define org-mode-map "so"     'org-schedule) in NL

(key-chord-define-global "sz"     'org-store-link)
(key-chord-define-global "sx"     'org-insert-link)

(key-chord-define org-agenda-mode-map "lo"
		  'org-agenda-open-link)
(key-chord-define org-agenda-mode-map "-p"
		  'org-agenda-drag-line-forward)
(key-chord-define org-agenda-mode-map "=["
		  'org-agenda-drag-line-backward)
(key-chord-define org-agenda-mode-map "za"
		  'org-agenda-toggle-archive-tag)

;; Clock In-Out and Timers
(key-chord-define-global "ce"     'org-clock-in-last)
(key-chord-define-global "cq"     'org-clock-out) ;; stop-clock

(key-chord-define python-mode-map "dt"     'org-babel-detangle)

;; Ivy and Counsel:
;; (key-chord-define Info-mode-map "df"     'counsel-describe-function)
;; (key-chord-define Info-mode-map "dv"     'counsel-describe-variable)
;; Helpful just purely eclipses counsel's features!

(key-chord-define ivy-minibuffer-map "gg"     'minibuffer-keyboard-quit) ;; often
(key-chord-define ivy-minibuffer-map "jj"     'ivy-next-line)
(key-chord-define ivy-minibuffer-map "kk"     'ivy-previous-line)
(key-chord-define ivy-minibuffer-map "km"     'ivy-scroll-up-command)
(key-chord-define ivy-minibuffer-map "ij"     'ivy-scroll-down-command)
(key-chord-define ivy-minibuffer-map "xx"     'hydra-ivy/body) ;; just sample


;; helpful ===========  ***  =====================
;; it's just a brilliant composer of *Help* buffers
;; Note that the built-in `describe-function' includes both functions
;; and macros. `helpful-function' is functions only, so we provide
;; `helpful-callable' as a drop-in replacement.
(global-set-key (kbd "C-h f") #'helpful-callable)

(global-set-key (kbd "C-h v") #'helpful-variable)
(global-set-key (kbd "C-h k") #'helpful-key)
(global-set-key (kbd "C-h x") #'helpful-command)

;; Lookup the current symbol at point. C-c C-d is a common keybinding
;; for this in lisp modes.
;; (global-set-key (kbd "C-c C-d") #'helpful-at-point)

;; Look up *F*unctions (excludes macros).
;;
;; By default, C-h F is bound to `Info-goto-emacs-command-node'. Helpful
;; already links to the manual, if a function is referenced there.
(global-set-key (kbd "C-h F") #'helpful-function)

(setq counsel-describe-function-function #'helpful-callable)
(setq counsel-describe-variable-function #'helpful-variable)
;; ======================  =========================

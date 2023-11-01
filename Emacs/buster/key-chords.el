;; KeyChords are below
;; General commants

;; Cursor Movement:
(key-chord-define-global "j;"     'move-end-of-line)
(key-chord-define-global "fa"     'move-beginning-of-line)
(key-chord-define-global "fd"     'left-word)

;; Scrolling
(key-chord-define-global "ij"     'scroll-down-command)
(key-chord-define-global ",j"     'scroll-up-command)

;; Frames and Windows management:
(key-chord-define-global "'\\"     'other-frame)
(key-chord-define-global "]\\"     'other-frame)
(key-chord-define-global "';"     'other-frame)
(key-chord-define-global "q1"     'delete-other-windows)
(key-chord-define-global "w2"     'split-window-below)
(key-chord-define-global "e3"     'split-window-right)
(key-chord-define-global "0o"     'delete-window)
(key-chord-define-global "oj"     'other-window)
(key-chord-define-global "OJ"
			 (lambda ()
			   (interactive) (other-window -1)))
(key-chord-define-global "}|"
			 (lambda ()
			   (interactive) (other-frame -1)))
(key-chord-define-global "rw"     'window-configuration-to-register)
(key-chord-define-global "rj"     'jump-to-register)
(key-chord-define-global "fm"     'follow-mode)
;; Buffers
(key-chord-define-global "bn"     'list-buffers)
(key-chord-define-global "bv"     'switch-to-buffer)
(key-chord-define-global "fq"     'previous-buffer)
(key-chord-define-global "jp"     'next-buffer)
(key-chord-define-global "bk"     'kill-buffer)
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
;; Marks
(key-chord-define-global "mk"     'set-mark-command)
(key-chord-define-global "m "     'set-mark-command)
;; Misc
(key-chord-define-global "fg"     'find-file)
(key-chord-define-global "ew"     'eval-last-sexp)
(key-chord-define-global "hg"     'keyboard-quit)
(key-chord-define-global "dc"     'with-editor-finish)
(key-chord-define-global "gs"     'magit-status)
(key-chord-define-global "vl"     'vc-print-log)
;;
;; (key-chord-define-global "ri"     'insert-register) ;; too common

;; Killing and Yanking
(key-chord-define-global "vf"     'kill-ring-save)
(key-chord-define-global "rf"     'kill-region)
(key-chord-define-global "uy"     'yank)
;; Translation
(key-chord-define-global "tr"     'google-translate-at-point)
(key-chord-define-global "ty"     'voca-builder/search-popup)
(key-chord-define-global "wt"     'dictionary-lookup-definition)
(key-chord-define-global "wd"     'mw-thesaurus-lookup-dwim)
    ;; (global-set-key "\C-x4w" 'langtool-check)
    ;; (global-set-key "\C-x4W" 'langtool-check-done)
    ;; (global-set-key "\C-x4l" 'langtool-switch-default-language)
    ;; (global-set-key "\C-x44" 'langtool-show-message-at-point)
    ;; (global-set-key "\C-x4c" 'langtool-correct-buffer)

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
(global-set-key (kbd "C-c a") 'org-agenda)
(key-chord-define-global "qq"     'org-fill-paragraph)
(key-chord-define org-mode-map "km"     'org-meta-return)
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
(key-chord-define-global "lc"     'org-clock-in-last)
(key-chord-define-global "sc"     'org-clock-out) ;; stop-clock

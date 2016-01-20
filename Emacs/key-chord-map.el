(key-chord-define-global "uu"     'undo)
;; single movement
(key-chord-define-global "jk"     'forward-char)
(key-chord-define-global "fd"     'backward-char)
(key-chord-define-global "ui"     'previous-line)
(key-chord-define-global "m,"     'next-line)
;; multi movement
(key-chord-define-global "jl"     'forward-word)
(key-chord-define-global "fs"     'backward-word)
(key-chord-define-global "uo"     'backward-paragraph)
(key-chord-define-global "m."     'forward-paragraph)
(key-chord-define-global "<<"     'beginning-of-buffer)
(key-chord-define-global ">>"     'end-of-buffer)
(key-chord-define-global "tt"     'scroll-down-command)
(key-chord-define-global "vv"     'scroll-up-command)
;; deleting and yanking
(key-chord-define-global "ww"     'kill-region)
(key-chord-define-global "WW"     'kill-ring-save)
(key-chord-define-global "yy"     'yank)
(key-chord-define-global "YY"     'yank-pop)
;; switch buffer
(key-chord-define-global "oo"     'other-window)
;(key-chord-define-global "OO"     "/C-o/C-o")
;(key-chord-define-global "op"     "/C-u/2/C-o")
(key-chord-define-global "bb"     'list-buffers)
(key-chord-define-global "BB"     'switch-to-buffer)
;; save all
(key-chord-define-global "ss"     'save-some-buffers)
(key-chord-define-global "SS"     'save-buffer)
;; deletion
(key-chord-define-global "gf"     'kill-word)
(key-chord-define-global "hj"     'backward-kill-word)
(key-chord-define-global "kl"     'kill-line)
;;
(provide 'key-chord-map)

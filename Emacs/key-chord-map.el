(key-chord-define-global "hj"     'undo)
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
;;
;;
(provide 'key-chord-map)

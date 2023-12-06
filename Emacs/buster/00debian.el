;; sudo chown <username> /etc/emacs/site-start.d/00debian.el
(tool-bar-mode -1)
(menu-bar-mode -1)
(scroll-bar-mode -1)

;; 55.04665127097639, -7.565092591636581
;; Baile Uí Fhloinn
;; (setq calendar-latitude 47.5)
;;    (setq calendar-longitude 34.65)
;;    (setq calendar-location-name "Energodar, ZP")
(setq calendar-latitude 55.0466)
   (setq calendar-longitude -7.5651)
   (setq calendar-location-name "Baile Uí Fhloinn, Co. Donegal")

(require 'package)
(add-to-list 'package-archives '("elpa" .
				 "https://elpa.gnu.org/packages/") t)
(add-to-list 'package-archives '("melpa" .
				 "https://melpa.org/packages/") t)
(package-initialize)

(load-theme 'manoj-dark);;tsdh-dark);;wombat)

(require 'org)
(require 'org-agenda)
(require 'org-tempo)
(require 'org-bullets)
(add-hook 'org-mode-hook (lambda () (org-bullets-mode 1)))
(require 'key-chord)
(key-chord-mode 1)
(add-to-list 'load-path "~/git/bookmark-plus/")
(require 'bookmark+)
(require 'magit)
(require 'google-translate)
(setq google-translate-translation-directions-alist '(("en" . "ru")))
(setq google-translate-default-source-language "en")
(setq google-translate-default-target-language "ru")
(require 'voca-builder)
(setq voca-builder/voca-file "~/git/lib/org/vocabulary/202309.org")
(setq voca-builder/export-file "~/.voca-builder-temp.org")
(setq voca-builder/current-tag "48")
(setq voca-builder/current-tag "sattelite")
(setq voca-builder/current-tag "misc")
(require 'elpy)
(require 'ereader)
(require 'howdoi)
(require 'org-drill)
(require 'mw-thesaurus)
(require 'dictionary)
(require 'pyvenv)
;;(pyvenv-activate "/home/alioth/.emacs.d/elpy/rpc-venv/") ;; restricted by elpy
(elpy-enable)
(org-clock-auto-clockout-insinuate)
(org-clock-toggle-auto-clockout)
;;(require 'langtool)
;; (setq langtool-language-tool-jar
;;       "/usr/local/java/LanguageTool-5.0/languagetool-commandline.jar")
;; (setq langtool-default-language "en-US")

;; Additional config section:
(load "~/.emacs.d/key-chords.el")

;; Org-capture templates in a separate file:
(load "~/.emacs.d/org-capture-templates.el")

;; Jekyll settings there -->
;;
(setq org-publish-project-alist
'(("jekyll-org"
   :base-directory "/home/alioth/git/org-pub/"
   :base-extension "org"
   ;; Path to your Jekyll project.
   :publishing-directory "/home/alioth/git/0--key.github.io/_posts/"
   :recursive t
   :publishing-function org-html-publish-to-html
   :headline-levels 4
   :html-extension "html"
   :section-numbers nil
   :with-toc nil
   :body-only t
   ;; Only export section between <body> </body> (body-only)
   )
  ("jekyll-org-img"
   :base-directory "/home/alioth/git/org-pub/img/"
   :base-extension "css\\|js\\|png\\|jpg\\|gif\\|pdf\\|mp3\\|ogg\\|swf\\|php"
   :publishing-directory "/home/alioth/git/0--key.io/assets/img/"
   :recursive t
   :publishing-function org-publish-attachment)

  ("jekyll" :components ("jekyll-org" "jekyll-org-img"))
  ))

;;
;; Out of the box section
;; Set the default mail server and news server as specified by Debian
;; policy.

(setq gnus-nntpserver-file "/etc/news/server")

(setq mail-host-address (let ((name (expand-file-name "/etc/mailname")))
                          (if (not (file-readable-p name))
                              nil
                            (with-temp-buffer
                              (insert-file-contents-literally name)
                              (while (search-forward "\n" nil t)
                                (replace-match "" nil t))
                              (buffer-string)))))

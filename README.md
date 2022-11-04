# FawsImageSearch: Anki Batch Download Image Search

**FawsImageSearch** is an Anki add-on to batch download images from an image search engine, such as Bing,
Google Images, etc. At the moment, it supports only Bing. It's based on a rewritten version of  
[batch-download-pictures-from-google-images](https://github.com/kelciour/batch-download-pictures-from-google-images).

TODO: Add a screenshot/gif

It works with the latest version of Anki at the time of writing
(2.1.54).

I wrote this add-on, because I waited for over six months for someone to
write something that would work with the latest version of Anki, but sadly,
nobody did. All other such add-ons:
* didn't work with the latest version of Anki
* rely on a brittle way to scrape Yandex, Google, etc. and stopped working years
    ago
* are not free

**Faws**: **F**ree **a**nd **w**orking **s**till.
 
## Installation
TODO: Add URL to our Anki page here.

## Why Bing instead of Google Images?
Currently, the add-on only works with **Bing Images**, though more
sources can easily be added (pull requests welcome).

### Non-programming explanation
Google doesn't want you to take pictures from Google Images using a program. For that reason, they're
constantly changing the structure of their site (most guides on the internet for
how to do this are outdated because it changes fairly frequently), which makes
any tool that scrapes Google Images brittle and easily broken.

Bing is much more friendly in this regard, which results in a more stable tool.

### Programming explanation
Barring SerpAPI, which is paid, there is pretty much no good way to scrape Google Images and
simultaneously have a robust and maintainable add-on. StackOverflow answers from one to two years ago at the time of writing are already outdated.

The [batch-download-pictures-from-google-images](https://github.com/kelciour/batch-download-pictures-from-google-images) (see the acknowledgements) add-on has code that, for example, is parsing the HTML as such:
```
for d in data[31][0][12][2]:
    try:
	results.append(d[1][3][0])
    except Exception as e:
	pass
```

This is by no means meant to shade the original author -- my point is that
there's no avoiding something like that based on how Google has structured their
page results, so this is about the best it can get. 

If the site being scraped eventually changes their format, I don't
want to go spend time to find out whether the 33rd or 34th index of the
array is the one that contains image data (and repeat this process multiple
times throughout the page). In short, Bing has somewhat lower
quality of images but a more maintainable way of accessing the images.

## Installation from source

See [this
thread](https://forums.ankiweb.net/t/add-support-for-dependencies-in-addons/24302/2).

```
pip3 install Pillow -t vendor
```

After that, move this directory to the Anki add-ons folder. This is covered in
the official documentation.

## Report a bug
Bugs can be reported either by filing an issue or contacting me at the email on my Github.

## Contributing
Pull requests are welcome. Feel free to first open an issue for discussion.

## Acknowledgements
Big thanks goes to @kelciour, who created the
[batch-download-pictures-from-google-images](https://github.com/kelciour/batch-download-pictures-from-google-images)
(doesn't work in newer versions of Anki). Much of the code was modeled off of
his repository.


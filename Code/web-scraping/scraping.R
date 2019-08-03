#import libraries
library('rvest')

#sink the output
sink("output.txt")
pac <- read_html("http://programsandcourses.anu.edu.au/2018/course/COMP3620/")

#pack desciption
description <- pac %>%
  #  html_nodes("intro__degree-description__text") %>%
  #  html_nodes(".copy p") %>%
  html_nodes("#introduction p") %>%
  html_text() %>%
  as.array()
description  

#learning <- pac %>%
#  html_nodes("#overview h2") %>%
#  html_text() %>%
#  as.array()
#learning

#learn_desc <- pac %>%
#  html_nodes("ol") %>%
#  html_text() %>%
#  as.list()
#learn_desc

#req <- pac %>%
#  html_nodes(".requisite") %>%
#  html_text() %>%
#  as.array()
#req

#url read
#require(rvest)
#urls <- c("http://programsandcourses.anu.edu.au/2018/course/COMP3620")

#loop body
#out <- vector("character", length = length(urls))
#for(i in seq_along(urls)){
#  derby  <- read_html(urls[i])
#  out[i] <- derby %>%
#    html_node("#introduction p") %>%
#    html_text() %>%
#    as.array()
#}

#set computing var
computing <- c ("COMP4560", "COMP3560",
                "COMP2550",
                "COMP3550",
                "COMP4450",
                "COMP4550",
                "COMP3620",
                "COMP4660",
                "COMP3310",
                "COMP2300",
                "COMP3820",
                "COMP4005F",
                "COMP4005P",
                "COMP3425",
                "COMP5920",
                "COMP3320",
                "COMP3770",
                "COMP4800",
                "COMP2420",
                "COMP4670",
                "COMP2620",
                "COMP3120",
                "COMP4130",
                "COMP2410",
                "COMP3702",
                "COMP1100",
                "COMP1130",
                "COMP1730",
                "COMP3740",
                "COMP2100",
                "COMP4500",
                "COMP3500",
                "COMP4540",
                "COMP2710",
                "COMP1110",
                "COMP3630",
                "COMP3710",
                "COMP1710"
)
for(k in computing) {
  
  loopsite <- paste("https://programsandcourses.anu.edu.au/2018/course/",k)
  loopsite <- read_html(loopsite)
  #download.file(loopsite, destfile = "C://Users//Yong Wei//Desktop//scrapedpage.html", quiet=TRUE)
  #content <- read_html("C://Users//Yong Wei//Desktop//scrapedpage.html")
  out[k] <- derby %>%
    html_node("#introduction p") %>%
    html_text() %>%
    as.array()
}
#Error in open.connection(x, "rb") : HTTP error 400.

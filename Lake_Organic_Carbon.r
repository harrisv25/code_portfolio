install.packages("earth")
library(earth)
install.packages("rsample")
library(rsample)
library(ggplot2)
install.packages("caret")
library(caret)
install.packages("vip")
library(vip)
library(pdp)
#build a segmented model
install.packages("segmented")
library(segmented)


#accessing a csv of lake sediment data
setwd("#####")

table=read.csv("####.csv")
attach(table)
names(table)

#spliting the dataset into test and validation samples
set.seed(123)
lily_split <- initial_split(table, prop = .7, strata = organics)
lily_train <- training(lily_split)
lily_test  <- testing(lily_split)

detach(w_train)
attach(lily_train)

#vissualize the data as a continuous line
p <- ggplot(lily_train, aes(x = Mean, y = organics)) + geom_line()

model=lm(organics~Mean)

my.coef <- coef(model)

p <- p + geom_abline(intercept = my.coef[1], 
                     slope = my.coef[2], 
                     aes(colour = "blue"))

summary(model)

#validate the model against the test sample
predictions <- model %>% predict(lily_test)
data.frame( R2 = R2(predictions, lily_test$organics),
            RMSE = RMSE(predictions, lily_test$organics),
            MAE = MAE(predictions, lily_test$organics))




my.seg= segmented(model, 
                  seg.Z = ~ Mean, 
                  psi = list(Mean = c(-38,  177, 417, 2000, 3000)))

summary(my.seg)
my.seg$psi
slope(my.seg)



# get the fitted data
my.fitted <- fitted(my.seg)
my.model <- data.frame(Distance = Mean, Elevation = my.fitted)

# plot the fitted model
ggplot(my.model, aes(x = Distance, y = Elevation)) + geom_line()


p + geom_line(data = my.model, aes(x = Distance, y = Elevation), colour = "tomato")


predictions <- my.seg %>% predict(lily_test)
data.frame( R2 = R2(predictions, lily_test$organics),
            RMSE = RMSE(predictions, lily_test$organics),
            MAE = MAE(predictions, lily_test$organics))




plot(organics~Depth)

p2 <- ggplot(lily_train, aes(x = Depth, y = organics)) + geom_line()

model2=lm(organics~Depth)

my.coef2 <- coef(model2)

p2 <- p2 + geom_abline(intercept = my.coef2[1], 
                       slope = my.coef2[2], 
                       aes(colour = "blue"))

my.seg2= segmented(model2, 
                   seg.Z = ~ Depth, 
                   psi = list(Depth = c(9, 20, 35)))

summary(my.seg2)
my.seg2$psi
slope(my.seg2)



# get the fitted data
my.fitted2 <- fitted(my.seg2)
my.model2 <- data.frame(Distance = Depth, Elevation = my.fitted2)

# plot the fitted model
ggplot(my.model2, aes(x = Distance, y = Elevation)) + geom_line()


p2 + geom_line(data = my.model2, aes(x = Distance, y = Elevation), colour = "tomato")

detach(lily_train)


predictions <- my.seg2 %>% predict(lily_test)
data.frame( R2 = R2(predictions, lily_test$organics),
            RMSE = RMSE(predictions, lily_test$organics),
            MAE = MAE(predictions, lily_test$organics))

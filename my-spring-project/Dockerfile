FROM maven:3.6.3-jdk-11

COPY ./ ./

RUN mvn clean package

EXPOSE 8080
EXPOSE 7200
## per evitare che si generi l'eccezione su core dump, messa la variabile qui sotto https://stackoverflow.com/questions/69347796/docker-run-failed-when-creating-container-with-spring-bootbuild-image-in-java-8
ENV BPL_JAVA_NMT_ENABLED=false
CMD ["java", "-jar", "target/my-spring-project-0.0.1-SNAPSHOT.jar"]

package com.example.spring.demo.controllers.queries;


import com.example.spring.demo.model.Triple;
import com.example.spring.demo.svg.UpdateOntologyFiletoRepository;
import org.springframework.web.bind.annotation.*;

import java.io.IOException;
import java.util.List;

@CrossOrigin
@RestController
@RequestMapping("/queries")
public class ControllerQueries {


  @GetMapping("/get")
  //http://localhost:8080/spring-app/queries/get?query=a
  public List<List<String>> get(@RequestParam String query) throws IOException {

    System.err.println(query);
    List<List<String>> queryResult = UpdateOntologyFiletoRepository.runQuery(UpdateOntologyFiletoRepository.getRepositoryConnection(), query);

    if (!queryResult.isEmpty()) {
      System.out.println(queryResult);
    }
    return queryResult;

  }


  @GetMapping("/get_list_of_triple")
  //http://localhost:8080/spring-app/queries/get?query=a
  public List<Triple> getReturnListOfObject(@RequestParam String query) throws IOException {

    System.err.println("get_list_of_triple called");

    System.err.println(query);

    System.err.println("ooooo" + UpdateOntologyFiletoRepository.getRepositoryConnection());

    List<Triple> listOfTriple = UpdateOntologyFiletoRepository.runQueryReturnListOfObject(UpdateOntologyFiletoRepository.getRepositoryConnection(), query);

    System.out.println("Problem");

    if (!listOfTriple.isEmpty()) {
      System.out.println(listOfTriple);
      System.out.println(listOfTriple.size());
    }
    return listOfTriple;

  }


  @GetMapping("/delete_everythings")
  //http://localhost:8080/spring-app/queries/delete_everythings
  public void delete() throws IOException {

    UpdateOntologyFiletoRepository.deleteEverythingFromRepository(UpdateOntologyFiletoRepository.getRepositoryConnection());

  }

}

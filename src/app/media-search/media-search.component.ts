import { Component, OnInit } from '@angular/core';

import { LocationService } from '../location.service';
import { MemberService } from '../member.service';

import { Globals } from '../globals';

@Component({
  selector: 'app-media-search',
  templateUrl: './media-search.component.html',
  styleUrls: ['./media-search.component.css']
})
export class MediaSearchComponent implements OnInit {
  suggested: any[] = [];
  items: any[] = [];
  cont: number = 0;
  
  msg: string = 0;
  query: string;
  
  title: string;
  author: string;
  genre: string;
  type_: string;
  
  constructor(
    private globals: Globals,
    private locationService: LocationService,
    private memberService: MemberService
  ) {}

  ngOnInit() {
    this.getSuggestions();
 // this.getAllItems(); // Do I really want this or should I limit it just to searches?
  }
  
  getSuggestions() {
    this.memberService.getSuggestions(this.cont)
      .subscribe(res => this.suggested = res, err => this.msg = err.error?err.error:'Error.');
  }
  
  getAllItems() {
    this.locationService.getItems
  }
  
  search(cont, title, author, genre, type_) {
    if (![title, author, genre, type_].some(n => n)) {
      this.getAllItems();
      return null;
    }
    
    this.locationService.searchMedia(cont, title, author, genre, type_)
      .subscribe(
        resp => {
          this.query = {page: cont/20, title: title, author: author, genre: genre, type_: type_}
          this.items = resp;
        },
        err => {
          this.msg = err.error?err.error:'Error.';
        }
      );
  }

}

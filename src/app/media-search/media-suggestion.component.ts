import { Component, OnInit, Input } from '@angular/core';

import { MemberService } from '../member.service';

import { Globals } from '../globals';

@Component({
  selector: 'media-suggestion',
  templateUrl: './media-suggestion.component.html',
  styleUrls: ['./media-search.component.css']
})
export class MediaSuggestionComponent implements OnInit {
  suggested: any[] = [];
  msg: string;
  @Input() heading: string;
  
  constructor(
    public globals: Globals,
    private memberService: MemberService
  ) {}
  
  ngOnInit() {
    this.getSuggestions();
  }
  
  getSuggestions() {
    this.memberService.getSuggestions()
      .subscribe(res => this.suggested = res.items, err => this.msg = err.error?err.error:'Error.');
  }
}
